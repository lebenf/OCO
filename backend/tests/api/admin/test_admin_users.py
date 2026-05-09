# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_users_admin(auth_client: AsyncClient):
    resp = await auth_client.get("/api/admin/users")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(u["username"] == "admin" for u in data["items"])


@pytest.mark.asyncio
async def test_list_users_forbidden_for_member(client: AsyncClient, regular_user):
    login = await client.post("/api/auth/login", json={"username": "member", "password": "password123"})
    assert login.status_code == 200
    resp = await client.get("/api/admin/users")
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_create_user(auth_client: AsyncClient):
    resp = await auth_client.post("/api/admin/users", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "secret123",
        "is_system_admin": False,
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "newuser"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_update_user(auth_client: AsyncClient):
    # Create then update
    create = await auth_client.post("/api/admin/users", json={
        "username": "toupdate",
        "email": "toupdate@example.com",
        "password": "secret123",
    })
    uid = create.json()["id"]

    resp = await auth_client.put(f"/api/admin/users/{uid}", json={"preferred_language": "en"})
    assert resp.status_code == 200
    assert resp.json()["preferred_language"] == "en"


@pytest.mark.asyncio
async def test_deactivate_user(auth_client: AsyncClient):
    create = await auth_client.post("/api/admin/users", json={
        "username": "todelete",
        "email": "todelete@example.com",
        "password": "secret123",
    })
    uid = create.json()["id"]

    resp = await auth_client.delete(f"/api/admin/users/{uid}")
    assert resp.status_code == 204

    # Verify soft-delete: list still returns user but is_active=False
    users = await auth_client.get("/api/admin/users")
    user = next(u for u in users.json()["items"] if u["id"] == uid)
    assert user["is_active"] is False


@pytest.mark.asyncio
async def test_reset_password(auth_client: AsyncClient, client: AsyncClient):
    create = await auth_client.post("/api/admin/users", json={
        "username": "pwreset",
        "email": "pwreset@example.com",
        "password": "oldpass123",
    })
    uid = create.json()["id"]

    resp = await auth_client.post(f"/api/admin/users/{uid}/reset-password", json={"new_password": "newpass456"})
    assert resp.status_code == 204

    login = await client.post("/api/auth/login", json={"username": "pwreset", "password": "newpass456"})
    assert login.status_code == 200
