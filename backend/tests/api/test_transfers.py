# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.container import Container
from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.location import Location
from app.services.transfer_service import group_containers_ffd


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
async def house_with_dest(db_session: AsyncSession, admin_user):
    house = House(name="Transfer House", code_prefix="X", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))

    dest_house = House(name="Destination House", code_prefix="Y", created_by=admin_user.id)
    db_session.add(dest_house)
    await db_session.flush()

    dest_location = Location(house_id=dest_house.id, name="Soggiorno")
    db_session.add(dest_location)
    await db_session.commit()
    return house, dest_house, dest_location


@pytest.fixture
async def closed_container(db_session: AsyncSession, house_with_dest, admin_user):
    house, dest_house, dest_location = house_with_dest
    c = Container(
        house_id=house.id,
        code="X-001",
        status="closed",
        nesting_level=0,
        destination_location_id=dest_location.id,
        volume_liters=Decimal("50.0"),
        created_by=admin_user.id,
    )
    db_session.add(c)
    await db_session.commit()
    return c


@pytest.fixture
async def transfer_client(auth_client: AsyncClient, house_with_dest):
    house, dest_house, dest_location = house_with_dest
    return auth_client, house, dest_house, dest_location


# ── FFD algorithm unit tests ───────────────────────────────────────────────────

from types import SimpleNamespace


def make_container(vol: float | None):
    return SimpleNamespace(
        id="fake",
        volume_liters=Decimal(str(vol)) if vol is not None else None,
    )


def test_ffd_single_bin():
    containers = [make_container(30), make_container(40), make_container(20)]
    bins, unassigned = group_containers_ffd(containers, 100)
    assert len(bins) == 1
    assert len(bins[0]) == 3
    assert unassigned == []


def test_ffd_two_bins():
    containers = [make_container(60), make_container(60), make_container(60)]
    bins, unassigned = group_containers_ffd(containers, 100)
    assert len(bins) == 3  # 60, 60, 60 — none fit together


def test_ffd_two_bins_pack():
    containers = [make_container(50), make_container(50), make_container(30), make_container(20)]
    bins, unassigned = group_containers_ffd(containers, 100)
    assert len(bins) == 2
    assert unassigned == []


def test_ffd_without_volume_unassigned():
    containers = [make_container(50), make_container(None), make_container(0)]
    bins, unassigned = group_containers_ffd(containers, 100)
    assert len(bins) == 1
    assert len(unassigned) == 2


def test_ffd_empty_list():
    bins, unassigned = group_containers_ffd([], 100)
    assert bins == []
    assert unassigned == []


# ── API tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_transfer(transfer_client, closed_container):
    client, house, dest_house, dest_location = transfer_client
    resp = await client.post(
        f"/api/houses/{house.id}/transfers",
        json={
            "name": "Primo viaggio",
            "destination_location_id": dest_location.id,
            "container_ids": [closed_container.id],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Primo viaggio"
    assert data["status"] == "planned"
    assert data["container_count"] == 1
    assert len(data["containers"]) == 1


@pytest.mark.asyncio
async def test_list_transfers_empty(transfer_client):
    client, house, dest_house, dest_location = transfer_client
    resp = await client.get(f"/api/houses/{house.id}/transfers")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_list_transfers_status_filter(transfer_client, closed_container):
    client, house, dest_house, dest_location = transfer_client
    await client.post(
        f"/api/houses/{house.id}/transfers",
        json={"name": "T1", "destination_location_id": dest_location.id},
    )
    resp = await client.get(f"/api/houses/{house.id}/transfers?status=planned")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    resp2 = await client.get(f"/api/houses/{house.id}/transfers?status=completed")
    assert resp2.status_code == 200
    assert len(resp2.json()) == 0


@pytest.mark.asyncio
async def test_get_transfer_detail(transfer_client, closed_container):
    client, house, dest_house, dest_location = transfer_client
    create_resp = await client.post(
        f"/api/houses/{house.id}/transfers",
        json={"name": "Detail test", "destination_location_id": dest_location.id, "container_ids": [closed_container.id]},
    )
    transfer_id = create_resp.json()["id"]

    resp = await client.get(f"/api/houses/{house.id}/transfers/{transfer_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == transfer_id
    assert len(data["containers"]) == 1


@pytest.mark.asyncio
async def test_update_transfer(transfer_client):
    client, house, dest_house, dest_location = transfer_client
    create_resp = await client.post(
        f"/api/houses/{house.id}/transfers",
        json={"name": "Old name", "destination_location_id": dest_location.id},
    )
    transfer_id = create_resp.json()["id"]

    resp = await client.put(
        f"/api/houses/{house.id}/transfers/{transfer_id}",
        json={"name": "New name", "notes": "Some notes"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "New name"
    assert data["notes"] == "Some notes"


@pytest.mark.asyncio
async def test_add_remove_containers(transfer_client, closed_container):
    client, house, dest_house, dest_location = transfer_client
    create_resp = await client.post(
        f"/api/houses/{house.id}/transfers",
        json={"name": "T", "destination_location_id": dest_location.id},
    )
    transfer_id = create_resp.json()["id"]

    add_resp = await client.post(
        f"/api/houses/{house.id}/transfers/{transfer_id}/containers",
        json={"container_ids": [closed_container.id]},
    )
    assert add_resp.status_code == 200
    assert add_resp.json()["container_count"] == 1

    del_resp = await client.delete(
        f"/api/houses/{house.id}/transfers/{transfer_id}/containers/{closed_container.id}"
    )
    assert del_resp.status_code == 200
    assert del_resp.json()["container_count"] == 0


@pytest.mark.asyncio
async def test_start_transfer_sets_in_transit(transfer_client, closed_container, db_session):
    client, house, dest_house, dest_location = transfer_client
    create_resp = await client.post(
        f"/api/houses/{house.id}/transfers",
        json={"name": "Start test", "destination_location_id": dest_location.id, "container_ids": [closed_container.id]},
    )
    transfer_id = create_resp.json()["id"]

    resp = await client.post(f"/api/houses/{house.id}/transfers/{transfer_id}/start")
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_progress"

    await db_session.refresh(closed_container)
    assert closed_container.status == "in_transit"


@pytest.mark.asyncio
async def test_complete_transfer_updates_container_house(transfer_client, closed_container, db_session):
    client, house, dest_house, dest_location = transfer_client
    create_resp = await client.post(
        f"/api/houses/{house.id}/transfers",
        json={"name": "Complete test", "destination_location_id": dest_location.id, "container_ids": [closed_container.id]},
    )
    transfer_id = create_resp.json()["id"]
    await client.post(f"/api/houses/{house.id}/transfers/{transfer_id}/start")

    resp = await client.post(f"/api/houses/{house.id}/transfers/{transfer_id}/complete")
    assert resp.status_code == 200
    assert resp.json()["status"] == "completed"

    await db_session.refresh(closed_container)
    assert closed_container.status == "delivered"
    assert closed_container.house_id == dest_house.id
    assert closed_container.current_location_id == dest_location.id
    assert closed_container.destination_location_id is None


@pytest.mark.asyncio
async def test_invalid_state_transitions(transfer_client, closed_container):
    client, house, dest_house, dest_location = transfer_client
    create_resp = await client.post(
        f"/api/houses/{house.id}/transfers",
        json={"name": "State test", "destination_location_id": dest_location.id, "container_ids": [closed_container.id]},
    )
    transfer_id = create_resp.json()["id"]

    # Can't complete before starting
    resp = await client.post(f"/api/houses/{house.id}/transfers/{transfer_id}/complete")
    assert resp.status_code == 400

    # Start it
    await client.post(f"/api/houses/{house.id}/transfers/{transfer_id}/start")

    # Can't start again
    resp2 = await client.post(f"/api/houses/{house.id}/transfers/{transfer_id}/start")
    assert resp2.status_code == 400


@pytest.mark.asyncio
async def test_plan_transfers_ffd(transfer_client, db_session, admin_user):
    client, house, dest_house, dest_location = transfer_client

    # Create 3 containers: 60L, 60L, 40L with 100L vehicle → 2 trips
    for i, vol in enumerate([60, 60, 40]):
        c = Container(
            house_id=house.id,
            code=f"X-{10+i:03d}",
            status="closed",
            nesting_level=0,
            destination_location_id=dest_location.id,
            volume_liters=Decimal(str(vol)),
            created_by=admin_user.id,
        )
        db_session.add(c)
    await db_session.commit()

    resp = await client.post(
        f"/api/houses/{house.id}/transfers/plan",
        json={
            "destination_house_id": dest_house.id,
            "vehicle_volume_liters": 100,
            "scheduled_dates": ["2026-06-15", "2026-06-22"],
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["algorithm"] == "FFD"
    assert len(data["trips"]) == 2
    assert data["unassigned_containers"] == []


@pytest.mark.asyncio
async def test_plan_transfers_unassigned(transfer_client, db_session, admin_user):
    client, house, dest_house, dest_location = transfer_client

    # Container without volume → unassigned
    c = Container(
        house_id=house.id,
        code="X-020",
        status="closed",
        nesting_level=0,
        destination_location_id=dest_location.id,
        volume_liters=None,
        created_by=admin_user.id,
    )
    db_session.add(c)
    await db_session.commit()

    resp = await client.post(
        f"/api/houses/{house.id}/transfers/plan",
        json={"destination_house_id": dest_house.id, "vehicle_volume_liters": 1000},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["unassigned_containers"]) == 1
    assert data["trips"] == []


@pytest.mark.asyncio
async def test_location_summary(transfer_client, closed_container):
    client, house, dest_house, dest_location = transfer_client
    resp = await client.get(f"/api/houses/{house.id}/locations/{dest_location.id}/summary")
    assert resp.status_code == 200
    data = resp.json()
    assert data["location"]["id"] == dest_location.id
    assert data["container_count"] == 1
    assert data["transferred_count"] == 0
    assert data["total_volume_liters"] == 50.0


@pytest.mark.asyncio
async def test_transfer_not_found(transfer_client):
    client, house, dest_house, dest_location = transfer_client
    resp = await client.get(f"/api/houses/{house.id}/transfers/nonexistent")
    assert resp.status_code == 404
