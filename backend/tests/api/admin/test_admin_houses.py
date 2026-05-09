# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from httpx import AsyncClient


async def _create_house(client: AsyncClient, name: str = "Test House", prefix: str = "A") -> dict:
    resp = await client.post("/api/admin/houses", json={
        "name": name,
        "description": "Test",
        "code_prefix": prefix,
    })
    assert resp.status_code == 201
    return resp.json()


@pytest.mark.asyncio
async def test_create_and_list_houses(auth_client: AsyncClient):
    await _create_house(auth_client, "House Alpha", "A")
    resp = await auth_client.get("/api/admin/houses")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_update_house(auth_client: AsyncClient):
    house = await _create_house(auth_client, "Before", "B")
    resp = await auth_client.put(f"/api/admin/houses/{house['id']}", json={"name": "After"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "After"


@pytest.mark.asyncio
async def test_add_and_remove_member(auth_client: AsyncClient, regular_user):
    house = await _create_house(auth_client)
    resp = await auth_client.post(f"/api/admin/houses/{house['id']}/members", json={
        "user_id": regular_user.id,
        "role": "member",
    })
    assert resp.status_code == 201
    assert resp.json()["role"] == "member"

    members = await auth_client.get(f"/api/admin/houses/{house['id']}/members")
    assert any(m["user_id"] == regular_user.id for m in members.json())

    del_resp = await auth_client.delete(f"/api/admin/houses/{house['id']}/members/{regular_user.id}")
    assert del_resp.status_code == 204

    members_after = await auth_client.get(f"/api/admin/houses/{house['id']}/members")
    assert not any(m["user_id"] == regular_user.id for m in members_after.json())


@pytest.mark.asyncio
async def test_add_member_updates_role(auth_client: AsyncClient, regular_user):
    house = await _create_house(auth_client)
    await auth_client.post(f"/api/admin/houses/{house['id']}/members", json={
        "user_id": regular_user.id, "role": "member"
    })
    await auth_client.post(f"/api/admin/houses/{house['id']}/members", json={
        "user_id": regular_user.id, "role": "admin"
    })
    members = await auth_client.get(f"/api/admin/houses/{house['id']}/members")
    m = next(m for m in members.json() if m["user_id"] == regular_user.id)
    assert m["role"] == "admin"


@pytest.mark.asyncio
async def test_house_forbidden_for_member(client: AsyncClient, regular_user):
    login = await client.post("/api/auth/login", json={"username": "member", "password": "password123"})
    assert login.status_code == 200
    resp = await client.get("/api/admin/houses")
    assert resp.status_code == 403
