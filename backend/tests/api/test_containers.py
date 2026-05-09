# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import io
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.house import House
from app.models.house_membership import HouseMembership


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
async def house_with_member(db_session: AsyncSession, admin_user) -> House:
    house = House(name="Test House", code_prefix="T", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))
    await db_session.commit()
    return house


@pytest.fixture
async def container_client(auth_client: AsyncClient, house_with_member: House):
    return auth_client, house_with_member


# ── Code generation ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_code_generation_sequential(container_client):
    client, house = container_client
    codes = []
    for _ in range(3):
        resp = await client.post(f"/api/houses/{house.id}/containers", json={})
        assert resp.status_code == 201
        codes.append(resp.json()["code"])
    assert codes == ["T-001", "T-002", "T-003"]


@pytest.mark.asyncio
async def test_code_prefix_respected(auth_client: AsyncClient, db_session: AsyncSession, admin_user):
    house = House(name="B House", code_prefix="B", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))
    await db_session.commit()

    resp = await auth_client.post(f"/api/houses/{house.id}/containers", json={})
    assert resp.status_code == 201
    assert resp.json()["code"].startswith("B-")


# ── Nesting validation ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_nesting_level_assigned(container_client):
    client, house = container_client
    parent = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()
    assert parent["nesting_level"] == 0

    child = (await client.post(f"/api/houses/{house.id}/containers", json={"parent_id": parent["id"]})).json()
    assert child["nesting_level"] == 1

    grandchild = (await client.post(f"/api/houses/{house.id}/containers", json={"parent_id": child["id"]})).json()
    assert grandchild["nesting_level"] == 2


@pytest.mark.asyncio
async def test_nesting_max_depth_rejected(container_client):
    client, house = container_client
    parent = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()
    child = (await client.post(f"/api/houses/{house.id}/containers", json={"parent_id": parent["id"]})).json()
    grandchild = (await client.post(f"/api/houses/{house.id}/containers", json={"parent_id": child["id"]})).json()

    resp = await client.post(f"/api/houses/{house.id}/containers", json={"parent_id": grandchild["id"]})
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "MAX_NESTING_DEPTH"


# ── CRUD ──────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_containers(container_client):
    client, house = container_client
    await client.post(f"/api/houses/{house.id}/containers", json={})
    resp = await client.get(f"/api/houses/{house.id}/containers")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_list_containers_filter_status(container_client):
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()
    await client.post(f"/api/houses/{house.id}/containers/{c['id']}/close", json={})

    open_resp = await client.get(f"/api/houses/{house.id}/containers?status=open")
    closed_resp = await client.get(f"/api/houses/{house.id}/containers?status=closed")
    assert all(x["status"] == "open" for x in open_resp.json()["items"])
    assert any(x["status"] == "closed" for x in closed_resp.json()["items"])


@pytest.mark.asyncio
async def test_get_container_by_code(container_client):
    client, house = container_client
    created = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()
    code = created["code"]

    resp = await client.get(f"/api/houses/{house.id}/containers/{code}")
    assert resp.status_code == 200
    assert resp.json()["id"] == created["id"]


@pytest.mark.asyncio
async def test_get_container_unknown_code(container_client):
    client, house = container_client
    resp = await client.get(f"/api/houses/{house.id}/containers/X-999")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_update_container(container_client):
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()

    resp = await client.put(f"/api/houses/{house.id}/containers/{c['id']}", json={
        "description": "Updated", "width_cm": 60, "depth_cm": 40, "height_cm": 30
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["description"] == "Updated"
    assert data["volume_liters"] == pytest.approx(72.0)


@pytest.mark.asyncio
async def test_close_container(container_client):
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()

    resp = await client.post(f"/api/houses/{house.id}/containers/{c['id']}/close", json={})
    assert resp.status_code == 200
    assert resp.json()["status"] == "closed"


@pytest.mark.asyncio
async def test_seal_container(container_client):
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()
    await client.post(f"/api/houses/{house.id}/containers/{c['id']}/close", json={})

    resp = await client.post(f"/api/houses/{house.id}/containers/{c['id']}/seal", json={})
    assert resp.status_code == 200
    assert resp.json()["status"] == "sealed"


@pytest.mark.asyncio
async def test_seal_open_container_rejected(container_client):
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()
    resp = await client.post(f"/api/houses/{house.id}/containers/{c['id']}/seal", json={})
    assert resp.status_code == 400


# ── Volume calculation ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_volume_auto_calculated(container_client):
    client, house = container_client
    resp = await client.post(f"/api/houses/{house.id}/containers", json={
        "width_cm": 60, "depth_cm": 40, "height_cm": 50
    })
    assert resp.status_code == 201
    assert resp.json()["volume_liters"] == pytest.approx(120.0)


# ── Photo upload ──────────────────────────────────────────────────────────────

def _make_jpeg_bytes() -> bytes:
    img = io.BytesIO()
    from PIL import Image as PILImage
    PILImage.new("RGB", (100, 100), color=(255, 0, 0)).save(img, "JPEG")
    return img.getvalue()


@pytest.mark.asyncio
async def test_photo_upload(container_client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()

    resp = await client.post(
        f"/api/houses/{house.id}/containers/{c['id']}/photos",
        files={"file": ("test.jpg", _make_jpeg_bytes(), "image/jpeg")},
        data={"phase": "empty"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["id"]
    assert data["phase"] == "empty"
    assert data["url"].startswith("/media/")


@pytest.mark.asyncio
async def test_photo_delete(container_client, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()

    upload = await client.post(
        f"/api/houses/{house.id}/containers/{c['id']}/photos",
        files={"file": ("test.jpg", _make_jpeg_bytes(), "image/jpeg")},
    )
    photo_id = upload.json()["id"]

    resp = await client.delete(f"/api/houses/{house.id}/containers/{c['id']}/photos/{photo_id}")
    assert resp.status_code == 204


# ── QR code ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_qr_code_returns_png(container_client):
    client, house = container_client
    c = (await client.post(f"/api/houses/{house.id}/containers", json={})).json()

    resp = await client.get(f"/api/houses/{house.id}/containers/{c['id']}/qr")
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "image/png"
    assert len(resp.content) > 0
    assert resp.content[:4] == b"\x89PNG"  # PNG magic bytes


# ── Access control ────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_non_member_cannot_access(client: AsyncClient, db_session: AsyncSession, admin_user, regular_user):
    house = House(name="Private", code_prefix="P", created_by=admin_user.id)
    db_session.add(house)
    await db_session.commit()

    login = await client.post("/api/auth/login", json={"username": "member", "password": "password123"})
    assert login.status_code == 200
    resp = await client.get(f"/api/houses/{house.id}/containers")
    assert resp.status_code == 403
