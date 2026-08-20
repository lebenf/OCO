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
from app.models.item import Item
from app.models.item_photo import ItemPhoto
from app.schemas.item import ItemCreate
from app.services.container_service import delete_container_with_files
from app.services.item_service import (
    _temp_photo_path,
    create_draft_item,
    create_draft_items_batch,
    delete_item_with_files,
    promote_temp_photos,
)


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


@pytest.mark.asyncio
async def test_new_photo_promoted_even_if_item_already_has_one(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    """Regression: a photo added meanwhile must not block promotion of a new one.

    This is what stranded 32 photos in temp/ in July — the item had picked up a
    photo from the edit view before the AI job finished, and the old guard then
    dropped the captured one entirely.
    """
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container

    with _ai_disabled():
        item, _ = await create_draft_item(
            container, house.id, ItemCreate(photo_ids=[], name="Casse"), admin_user.id, db_session
        )
    manual_dir = tmp_path / house.id / "items" / item.id
    manual_dir.mkdir(parents=True)
    (manual_dir / "manual.jpg").write_bytes(b"\xff\xd8\xff\xe0manual")
    db_session.add(ItemPhoto(
        item_id=item.id,
        file_path=str(Path(house.id) / "items" / item.id / "manual.jpg"),
        original_filename="from-gallery.jpg",
        mime_type="image/jpeg",
        file_size_bytes=6,
        sort_order=0,
        is_primary=True,
    ))
    await db_session.commit()

    rel_temp = _write_temp_photo(str(tmp_path), "photo-late")
    await promote_temp_photos(item, [rel_temp], db_session)
    await db_session.commit()

    photos = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id).order_by(ItemPhoto.sort_order)
    )).scalars().all()
    assert len(photos) == 2
    assert photos[0].is_primary and not photos[1].is_primary
    assert photos[1].sort_order == 1
    assert (tmp_path / photos[1].file_path).exists()
    assert not (tmp_path / rel_temp).exists()


@pytest.mark.asyncio
async def test_already_permanent_path_is_not_moved_again(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    """A retry job re-submits permanent paths; they must be ignored, not duplicated."""
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    rel_temp = _write_temp_photo(str(tmp_path), "photo-3")

    with _ai_disabled():
        item, _ = await create_draft_item(
            container, house.id, ItemCreate(photo_ids=["photo-3"]), admin_user.id, db_session
        )
    permanent = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalar_one().file_path

    await promote_temp_photos(item, [permanent], db_session)
    await db_session.commit()

    photos = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalars().all()
    assert len(photos) == 1
    assert (tmp_path / permanent).exists()
    assert not (tmp_path / rel_temp).exists()


@pytest.mark.asyncio
async def test_path_outside_temp_is_rejected(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    """photo_ids come from the client; a crafted id must not pull in outside files."""
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    (tmp_path / "temp").mkdir(parents=True, exist_ok=True)
    secret = tmp_path.parent / "secret.jpg"
    secret.write_bytes(b"\xff\xd8\xff\xe0secret")

    item = Item(
        house_id=house.id, container_id=container.id, created_by=admin_user.id,
        name="x", item_type="single", status="confirmed",
    )
    db_session.add(item)
    await db_session.flush()

    await promote_temp_photos(item, [_temp_photo_path("../../secret")], db_session)
    await db_session.commit()

    photos = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalars().all()
    assert photos == []
    assert secret.exists()


@pytest.mark.asyncio
async def test_delete_item_removes_photo_files(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    _write_temp_photo(str(tmp_path), "photo-4")

    with _ai_disabled():
        item, _ = await create_draft_item(
            container, house.id, ItemCreate(photo_ids=["photo-4"]), admin_user.id, db_session
        )
    photo_path = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalar_one().file_path
    item_dir = tmp_path / house.id / "items" / item.id
    assert (tmp_path / photo_path).exists()

    await delete_item_with_files(item, db_session)

    assert not (tmp_path / photo_path).exists()
    assert not item_dir.exists()
    assert (await db_session.execute(select(ItemPhoto).where(ItemPhoto.item_id == item.id))).scalars().all() == []


@pytest.mark.asyncio
async def test_delete_container_removes_its_items_photo_files(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    _write_temp_photo(str(tmp_path), "photo-5")

    with _ai_disabled():
        item, _ = await create_draft_item(
            container, house.id, ItemCreate(photo_ids=["photo-5"]), admin_user.id, db_session
        )
    photo_path = (await db_session.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalar_one().file_path
    assert (tmp_path / photo_path).exists()

    await delete_container_with_files(container, db_session)

    assert not (tmp_path / photo_path).exists()
    assert await db_session.get(Item, item.id) is None
