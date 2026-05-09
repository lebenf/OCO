# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_login_ok(client: AsyncClient, admin_user):
    resp = await client.post("/api/auth/login", json={"username": "admin", "password": "password123"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["user"]["username"] == "admin"
    assert data["user"]["is_system_admin"] is True
    assert "access_token" in resp.cookies
    assert "refresh_token" in resp.cookies


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, admin_user):
    resp = await client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "INVALID_CREDENTIALS"


@pytest.mark.asyncio
async def test_login_unknown_user(client: AsyncClient):
    resp = await client.post("/api/auth/login", json={"username": "nobody", "password": "x"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_authenticated(auth_client: AsyncClient):
    resp = await auth_client.get("/api/auth/me")
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


@pytest.mark.asyncio
async def test_me_no_token(client: AsyncClient):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_update_language(auth_client: AsyncClient):
    resp = await auth_client.put("/api/auth/me", json={"preferred_language": "en"})
    assert resp.status_code == 200
    assert resp.json()["preferred_language"] == "en"


@pytest.mark.asyncio
async def test_logout(auth_client: AsyncClient):
    resp = await auth_client.post("/api/auth/logout")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    # access_token cookie should be cleared
    assert resp.cookies.get("access_token") is None or resp.cookies.get("access_token") == ""


@pytest.mark.asyncio
async def test_refresh_token(client: AsyncClient, admin_user):
    # Login to get cookies
    login_resp = await client.post("/api/auth/login", json={"username": "admin", "password": "password123"})
    assert login_resp.status_code == 200

    # Refresh
    resp = await client.post("/api/auth/refresh")
    assert resp.status_code == 200
    assert resp.json() == {"ok": True}
    assert "access_token" in resp.cookies


@pytest.mark.asyncio
async def test_refresh_no_token(client: AsyncClient):
    resp = await client.post("/api/auth/refresh")
    assert resp.status_code == 401
    assert resp.json()["detail"]["code"] == "MISSING_REFRESH_TOKEN"


@pytest.mark.asyncio
async def test_protected_route_requires_auth(client: AsyncClient):
    """Any auth-required endpoint returns 401 without cookie."""
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 401
