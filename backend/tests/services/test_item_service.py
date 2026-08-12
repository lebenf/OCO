# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pathlib import Path
from unittest.mock import patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.container import Container
from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.item_photo import ItemPhoto
from app.schemas.item import ItemCreate
from app.services.item_service import create_draft_item, create_draft_items_batch


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
async def house_with_container(db_session: AsyncSession, admin_user):
    house = House(name="Test House", code_prefix="T", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))
    await db_session.flush()

    container = Container(
        house_id=house.id,
        code="T-001",
        status="open",
        nesting_level=0,
        created_by=admin_user.id,
    )
    db_session.add(container)
    await db_session.commit()
    return house, container


def _write_temp_photo(storage_path: str, photo_id: str) -> str:
    rel_path = str(Path("temp") / f"{photo_id}.jpg")
    abs_path = Path(storage_path) / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-bytes")
    return rel_path


def _ai_disabled():
    return patch(
        "app.services.item_service.get_live_config",
        return_value={"ai_enrichment_enabled": False},
    )


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_photos_promoted_when_ai_disabled(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    """With AI enrichment off no job runs, so creation itself must persist the photos."""
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    rel_temp = _write_temp_photo(str(tmp_path), "photo-1")

    with _ai_disabled():
        item, job = await create_draft_item(
            container,
            house.id,
            ItemCreate(photo_ids=["photo-1"], name="Set Duplo"),
            admin_user.id,
            db_session,
        )

    assert job is None
    assert item.status == "confirmed"
    photos = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalars().all()
    assert len(photos) == 1
    assert photos[0].is_primary
    assert (tmp_path / photos[0].file_path).exists()
    assert not (tmp_path / rel_temp).exists()


@pytest.mark.asyncio
async def test_batch_photos_promoted_when_ai_disabled(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    _write_temp_photo(str(tmp_path), "photo-a")
    _write_temp_photo(str(tmp_path), "photo-b")

    with _ai_disabled():
        results = await create_draft_items_batch(
            container,
            house.id,
            [
                ItemCreate(photo_ids=["photo-a"], name="Gioco Elefun"),
                ItemCreate(photo_ids=["photo-b"], name="Resina epoxy"),
            ],
            admin_user.id,
            db_session,
        )

    assert [job for _, job in results] == [None, None]
    for item, _ in results:
        photos = (await db_session.execute(
            select(ItemPhoto).where(ItemPhoto.item_id == item.id)
        )).scalars().all()
        assert len(photos) == 1
        assert (tmp_path / photos[0].file_path).exists()


@pytest.mark.asyncio
async def test_photos_left_to_worker_when_ai_enabled(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    """With AI on the job owns promotion — creation must not move the files early."""
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    rel_temp = _write_temp_photo(str(tmp_path), "photo-2")

    with patch(
        "app.services.item_service.get_live_config",
        return_value={"ai_enrichment_enabled": True},
    ):
        item, job = await create_draft_item(
            container,
            house.id,
            ItemCreate(photo_ids=["photo-2"]),
            admin_user.id,
            db_session,
        )

    assert job is not None
    assert item.status == "draft"
    photos = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalars().all()
    assert photos == []
    assert (tmp_path / rel_temp).exists()
