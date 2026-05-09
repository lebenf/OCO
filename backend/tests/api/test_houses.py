# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.house import House
from app.models.house_membership import HouseMembership


async def _setup_house_with_admin(auth_client: AsyncClient) -> dict:
    """Create house and make admin a house admin member."""
    resp = await auth_client.post("/api/admin/houses", json={
        "name": "Config House", "code_prefix": "C"
    })
    return resp.json()


@pytest.mark.asyncio
async def test_location_crud(auth_client: AsyncClient, db_session: AsyncSession, admin_user):
    house_data = await _setup_house_with_admin(auth_client)
    house_id = house_data["id"]

    # Add admin as house admin
    db_session.add(HouseMembership(house_id=house_id, user_id=admin_user.id, role="admin"))
    await db_session.commit()

    # Create
    resp = await auth_client.post(f"/api/houses/{house_id}/locations", json={"name": "Cantina"})
    assert resp.status_code == 201
    loc_id = resp.json()["id"]

    # List
    resp = await auth_client.get(f"/api/houses/{house_id}/locations")
    assert resp.status_code == 200
    assert any(l["id"] == loc_id for l in resp.json())

    # Update
    resp = await auth_client.put(f"/api/houses/{house_id}/locations/{loc_id}", json={"name": "Garage"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Garage"

    # Delete
    resp = await auth_client.delete(f"/api/houses/{house_id}/locations/{loc_id}")
    assert resp.status_code == 204

    resp = await auth_client.get(f"/api/houses/{house_id}/locations")
    assert not any(l["id"] == loc_id for l in resp.json())


@pytest.mark.asyncio
async def test_all_locations(auth_client: AsyncClient, db_session: AsyncSession, admin_user):
    house_data = await _setup_house_with_admin(auth_client)
    house_id = house_data["id"]

    db_session.add(HouseMembership(house_id=house_id, user_id=admin_user.id, role="admin"))
    await db_session.commit()

    # Add a location to the house
    await auth_client.post(f"/api/houses/{house_id}/locations", json={"name": "Cantina"})

    resp = await auth_client.get("/api/houses/all-locations")
    assert resp.status_code == 200
    entries = resp.json()
    # Should include the house we just created with the location
    house_entry = next((e for e in entries if e["house"]["id"] == house_id), None)
    assert house_entry is not None
    assert any(loc["name"] == "Cantina" for loc in house_entry["locations"])


@pytest.mark.asyncio
async def test_member_cannot_manage_locations(client: AsyncClient, db_session: AsyncSession, regular_user, admin_user):
    # Create house as system admin
    from app.models.house import House as HouseModel
    house = HouseModel(name="H", code_prefix="H", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=regular_user.id, role="member"))
    await db_session.commit()

    login = await client.post("/api/auth/login", json={"username": "member", "password": "password123"})
    assert login.status_code == 200

    resp = await client.post(f"/api/houses/{house.id}/locations", json={"name": "Test"})
    assert resp.status_code == 403
