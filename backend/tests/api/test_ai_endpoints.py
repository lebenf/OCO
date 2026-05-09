# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import io
import pytest
from httpx import AsyncClient
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.ai_analysis_job import AIAnalysisJob
from app.models.container import Container
from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.item import Item


def _make_jpeg_bytes(width: int = 10, height: int = 10) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(100, 150, 200)).save(buf, format="JPEG")
    return buf.getvalue()


@pytest.fixture
async def ai_house(db_session: AsyncSession, admin_user):
    house = House(name="AIHouse", code_prefix="AI", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))
    await db_session.commit()
    return house


@pytest.mark.asyncio
async def test_upload_temp_photo(auth_client: AsyncClient, ai_house, tmp_path, monkeypatch):
    from app.core import config as cfg_module
    monkeypatch.setattr(cfg_module.settings, "STORAGE_PATH", str(tmp_path))

    resp = await auth_client.post(
        f"/api/houses/{ai_house.id}/ai/temp-photos",
        files=[("files", ("photo.jpg", _make_jpeg_bytes(), "image/jpeg"))],
    )
    assert resp.status_code == 201
    data = resp.json()
    assert len(data) == 1
    assert "id" in data[0]
    assert data[0]["url"].startswith("/media/temp/")


@pytest.mark.asyncio
async def test_upload_temp_photo_invalid(auth_client: AsyncClient, ai_house, tmp_path, monkeypatch):
    from app.core import config as cfg_module
    monkeypatch.setattr(cfg_module.settings, "STORAGE_PATH", str(tmp_path))

    resp = await auth_client.post(
        f"/api/houses/{ai_house.id}/ai/temp-photos",
        files=[("files", ("bad.jpg", b"not-an-image", "image/jpeg"))],
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_inbox_count_empty(auth_client: AsyncClient, ai_house):
    resp = await auth_client.get(f"/api/houses/{ai_house.id}/inbox/count")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 0
    assert data["pending_ai"] == 0
    assert data["ready_for_review"] == 0
    assert data["failed"] == 0


@pytest.mark.asyncio
async def test_inbox_count_with_items(auth_client: AsyncClient, ai_house, db_session: AsyncSession, admin_user):
    container = Container(
        house_id=ai_house.id, code="AI-001", status="open",
        nesting_level=0, created_by=admin_user.id,
    )
    db_session.add(container)
    await db_session.flush()

    items = [
        Item(house_id=ai_house.id, container_id=container.id, name="Draft",
             status="draft", item_type="single", quantity=1, created_by=admin_user.id),
        Item(house_id=ai_house.id, container_id=container.id, name="Done",
             status="draft_ai_done", item_type="single", quantity=1, created_by=admin_user.id),
        Item(house_id=ai_house.id, container_id=container.id, name="Failed",
             status="draft_ai_failed", item_type="single", quantity=1, created_by=admin_user.id),
    ]
    db_session.add_all(items)
    await db_session.commit()

    resp = await auth_client.get(f"/api/houses/{ai_house.id}/inbox/count")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3
    assert data["pending_ai"] == 1
    assert data["ready_for_review"] == 1
    assert data["failed"] == 1


@pytest.mark.asyncio
async def test_get_job_status(auth_client: AsyncClient, ai_house, db_session: AsyncSession, admin_user):
    container = Container(
        house_id=ai_house.id, code="AI-002", status="open",
        nesting_level=0, created_by=admin_user.id,
    )
    db_session.add(container)
    await db_session.flush()

    item = Item(
        house_id=ai_house.id, container_id=container.id, name="Item",
        status="draft", item_type="single", quantity=1, created_by=admin_user.id,
    )
    db_session.add(item)
    await db_session.flush()

    job = AIAnalysisJob(
        house_id=ai_house.id,
        item_id=item.id,
        status="completed",
        requested_by=admin_user.id,
    )
    db_session.add(job)
    await db_session.commit()

    resp = await auth_client.get(f"/api/houses/{ai_house.id}/ai/jobs/{job.id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == job.id
    assert data["status"] == "completed"
    assert data["item_id"] == item.id


@pytest.mark.asyncio
async def test_get_job_not_found(auth_client: AsyncClient, ai_house):
    resp = await auth_client.get(f"/api/houses/{ai_house.id}/ai/jobs/nonexistent")
    assert resp.status_code == 404
