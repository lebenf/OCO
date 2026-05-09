# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.container import Container
from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.item import Item
from app.models.location import Location
from app.models.transfer import Transfer


@pytest.fixture
async def dashboard_setup(db_session: AsyncSession, admin_user):
    house = House(name="DashHouse", code_prefix="D", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))

    dest_house = House(name="Destination House", code_prefix="E", created_by=admin_user.id)
    db_session.add(dest_house)
    await db_session.flush()

    dest_location = Location(house_id=dest_house.id, name="Soggiorno")
    db_session.add(dest_location)
    await db_session.flush()

    c1 = Container(house_id=house.id, code="D-001", status="open", nesting_level=0, created_by=admin_user.id)
    c2 = Container(house_id=house.id, code="D-002", status="closed", nesting_level=0,
                   destination_location_id=dest_location.id, volume_liters=Decimal("80.0"), created_by=admin_user.id)
    c3 = Container(house_id=house.id, code="D-003", status="sealed", nesting_level=0,
                   destination_location_id=dest_location.id, volume_liters=Decimal("60.0"), created_by=admin_user.id)
    db_session.add_all([c1, c2, c3])
    await db_session.flush()

    item = Item(
        house_id=house.id, container_id=c1.id, name="Test Item", status="confirmed",
        item_type="single", quantity=1, created_by=admin_user.id,
    )
    db_session.add(item)
    await db_session.commit()
    return house, dest_house, dest_location, [c1, c2, c3], item


@pytest.mark.asyncio
async def test_dashboard_structure(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/dashboard")
    assert resp.status_code == 200
    data = resp.json()

    assert "containers" in data
    assert data["containers"]["total"] == 3
    assert "open" in data["containers"]["by_status"]
    assert data["containers"]["by_status"]["open"] == 1
    assert data["containers"]["by_status"]["closed"] == 1
    assert data["containers"]["by_status"]["sealed"] == 1


@pytest.mark.asyncio
async def test_dashboard_items_count(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"]["total"] == 1


@pytest.mark.asyncio
async def test_dashboard_by_destination_house(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/dashboard")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["by_destination_house"]) == 1
    stat = data["by_destination_house"][0]
    assert stat["house"]["id"] == dest_house.id
    assert stat["container_count"] == 2
    assert stat["total_volume_liters"] == 140.0
    assert stat["delivered"] == 0


@pytest.mark.asyncio
async def test_dashboard_upcoming_transfers(auth_client: AsyncClient, dashboard_setup, db_session):
    house, dest_house, dest_location, containers, item = dashboard_setup
    t = Transfer(
        house_id=house.id, name="Upcoming", destination_location_id=dest_location.id,
        status="planned", created_by=containers[0].created_by,
    )
    db_session.add(t)
    await db_session.commit()

    resp = await auth_client.get(f"/api/houses/{house.id}/dashboard")
    data = resp.json()
    assert len(data["upcoming_transfers"]) == 1


@pytest.mark.asyncio
async def test_dashboard_recent_containers(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/dashboard")
    data = resp.json()
    assert len(data["recent_containers"]) == 3


@pytest.mark.asyncio
async def test_search_items(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/search?q=Test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["query"] == "Test"
    assert len(data["items"]) == 1
    assert data["items"][0]["name"] == "Test Item"


@pytest.mark.asyncio
async def test_search_containers_by_code(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/search?q=D-00")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["containers"]) == 3


@pytest.mark.asyncio
async def test_search_min_length(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/search?q=a")
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_search_no_results(auth_client: AsyncClient, dashboard_setup):
    house, dest_house, dest_location, containers, item = dashboard_setup
    resp = await auth_client.get(f"/api/houses/{house.id}/search?q=zzznomatch")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"] == []
    assert data["containers"] == []
