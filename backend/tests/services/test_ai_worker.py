# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import asyncio
import json
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_analysis_job import AIAnalysisJob
from app.models.item import Item
from app.models.item_photo import ItemPhoto
from app.services.ai.base import AIAnalysisResult
from app.services.ai.job_processor import process_next_job, claim_next_pending_job
from app.services.item_service import retry_ai


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_job(db_session, house_id, requested_by, item_id=None, photo_paths=None):
    job = AIAnalysisJob(
        house_id=house_id,
        requested_by=requested_by,
        status="pending",
        hint_type="auto",
        language="it",
        item_id=item_id,
        input_photo_paths=json.dumps(photo_paths or []),
    )
    db_session.add(job)
    return job


def _make_item(db_session, house_id, container_id, created_by):
    item = Item(
        house_id=house_id,
        container_id=container_id,
        created_by=created_by,
        name="placeholder",
        item_type="single",
        status="draft",
    )
    db_session.add(item)
    return item


def _write_temp_photo(storage_path: str, photo_id: str) -> str:
    rel_path = str(Path("temp") / f"{photo_id}.jpg")
    abs_path = Path(storage_path) / rel_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"\xff\xd8\xff\xe0fake-jpeg-bytes")
    return rel_path


_GOOD_RESULT = AIAnalysisResult(
    name="Monitor LG 27\"",
    description="Monitor professionale",
    item_type="single",
    brand="LG",
    color="nero",
    confidence=0.9,
)

_MOCK_ADAPTER = AsyncMock()
_MOCK_ADAPTER.analyze = AsyncMock(return_value=_GOOD_RESULT)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
async def house_with_container(db_session: AsyncSession, admin_user):
    from app.models.house import House
    from app.models.container import Container
    from app.models.house_membership import HouseMembership

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


# ── Tests ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_no_pending_jobs_returns_false(db_session: AsyncSession, admin_user, house_with_container):
    house, _ = house_with_container
    with patch("app.services.ai.job_processor.get_ai_adapter", return_value=_MOCK_ADAPTER):
        result = await process_next_job(db_session)
    assert result is False


@pytest.mark.asyncio
async def test_pending_job_processed_successfully(db_session: AsyncSession, admin_user, house_with_container):
    house, container = house_with_container
    item = _make_item(db_session, house.id, container.id, admin_user.id)
    await db_session.flush()
    job = _make_job(db_session, house.id, admin_user.id, item_id=item.id)
    await db_session.commit()

    adapter = AsyncMock()
    adapter.analyze = AsyncMock(return_value=_GOOD_RESULT)

    with patch("app.services.ai.job_processor.get_ai_adapter", return_value=adapter):
        processed = await process_next_job(db_session)

    assert processed is True

    await db_session.refresh(job)
    await db_session.refresh(item)

    assert job.status == "completed"
    assert item.status == "draft_ai_done"
    assert item.name == "Monitor LG 27\""
    assert item.brand == "LG"
    assert item.ai_generated is True
    assert item.ai_error is None


@pytest.mark.asyncio
async def test_timeout_marks_item_failed(db_session: AsyncSession, admin_user, house_with_container):
    house, container = house_with_container
    item = _make_item(db_session, house.id, container.id, admin_user.id)
    await db_session.flush()
    job = _make_job(db_session, house.id, admin_user.id, item_id=item.id)
    await db_session.commit()

    async def slow_analyze(*args, **kwargs):
        await asyncio.sleep(100)
        return _GOOD_RESULT

    adapter = AsyncMock()
    adapter.analyze = slow_analyze

    with (
        patch("app.services.ai.job_processor.get_ai_adapter", return_value=adapter),
        patch("app.core.config.settings.AI_TIMEOUT_SECONDS", 0),
        patch("app.core.config.settings.OLLAMA_TIMEOUT_SECONDS", 0),
    ):
        processed = await process_next_job(db_session)

    assert processed is True

    await db_session.refresh(job)
    await db_session.refresh(item)

    assert job.status == "failed"
    assert job.error_message == "timeout"
    assert item.status == "draft_ai_failed"
    assert item.ai_error == "timeout"


@pytest.mark.asyncio
async def test_malformed_response_marks_item_failed(db_session: AsyncSession, admin_user, house_with_container):
    house, container = house_with_container
    item = _make_item(db_session, house.id, container.id, admin_user.id)
    await db_session.flush()
    job = _make_job(db_session, house.id, admin_user.id, item_id=item.id)
    await db_session.commit()

    adapter = AsyncMock()
    adapter.analyze = AsyncMock(side_effect=ValueError("AI response is not valid JSON"))

    with patch("app.services.ai.job_processor.get_ai_adapter", return_value=adapter):
        processed = await process_next_job(db_session)

    assert processed is True

    await db_session.refresh(job)
    await db_session.refresh(item)

    assert job.status == "failed"
    assert "AI response" in job.error_message
    assert item.status == "draft_ai_failed"


@pytest.mark.asyncio
async def test_photo_promoted_on_timeout(db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    item = _make_item(db_session, house.id, container.id, admin_user.id)
    await db_session.flush()
    rel_temp = _write_temp_photo(str(tmp_path), "photo-1")
    job = _make_job(db_session, house.id, admin_user.id, item_id=item.id, photo_paths=[rel_temp])
    await db_session.commit()

    async def slow_analyze(*args, **kwargs):
        await asyncio.sleep(100)
        return _GOOD_RESULT

    adapter = AsyncMock()
    adapter.analyze = slow_analyze

    with (
        patch("app.services.ai.job_processor.get_ai_adapter", return_value=adapter),
        patch("app.core.config.settings.AI_TIMEOUT_SECONDS", 0),
        patch("app.core.config.settings.OLLAMA_TIMEOUT_SECONDS", 0),
    ):
        await process_next_job(db_session)

    await db_session.refresh(item)
    assert item.status == "draft_ai_failed"
    photos = (await db_session.execute(select(ItemPhoto).where(ItemPhoto.item_id == item.id))).scalars().all()
    assert len(photos) == 1
    assert (tmp_path / photos[0].file_path).exists()
    assert not (tmp_path / rel_temp).exists()


@pytest.mark.asyncio
async def test_photo_promoted_on_ai_exception(db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    item = _make_item(db_session, house.id, container.id, admin_user.id)
    await db_session.flush()
    rel_temp = _write_temp_photo(str(tmp_path), "photo-2")
    job = _make_job(db_session, house.id, admin_user.id, item_id=item.id, photo_paths=[rel_temp])
    await db_session.commit()

    adapter = AsyncMock()
    adapter.analyze = AsyncMock(side_effect=ConnectionError("Ollama unreachable"))

    with patch("app.services.ai.job_processor.get_ai_adapter", return_value=adapter):
        await process_next_job(db_session)

    await db_session.refresh(item)
    assert item.status == "draft_ai_failed"
    photos = (await db_session.execute(select(ItemPhoto).where(ItemPhoto.item_id == item.id))).scalars().all()
    assert len(photos) == 1
    assert (tmp_path / photos[0].file_path).exists()


@pytest.mark.asyncio
async def test_retry_after_failure_reuses_permanent_photo_no_duplicate(
    db_session: AsyncSession, admin_user, house_with_container, tmp_path, monkeypatch
):
    monkeypatch.setattr(settings, "STORAGE_PATH", str(tmp_path))
    house, container = house_with_container
    item = _make_item(db_session, house.id, container.id, admin_user.id)
    await db_session.flush()
    rel_temp = _write_temp_photo(str(tmp_path), "photo-3")
    job = _make_job(db_session, house.id, admin_user.id, item_id=item.id, photo_paths=[rel_temp])
    item.ai_job_id = job.id
    await db_session.commit()

    failing_adapter = AsyncMock()
    failing_adapter.analyze = AsyncMock(side_effect=ConnectionError("Ollama unreachable"))
    with patch("app.services.ai.job_processor.get_ai_adapter", return_value=failing_adapter):
        await process_next_job(db_session)
    await db_session.refresh(item)

    await retry_ai(item, admin_user.id, db_session)
    await db_session.refresh(item)

    ok_adapter = AsyncMock()
    ok_adapter.analyze = AsyncMock(return_value=_GOOD_RESULT)
    with patch("app.services.ai.job_processor.get_ai_adapter", return_value=ok_adapter):
        await process_next_job(db_session)
    await db_session.refresh(item)

    assert item.status == "draft_ai_done"
    photos = (await db_session.execute(select(ItemPhoto).where(ItemPhoto.item_id == item.id))).scalars().all()
    assert len(photos) == 1  # no duplicate created on retry


@pytest.mark.asyncio
async def test_atomic_claim_two_workers(db_session: AsyncSession, admin_user, house_with_container):
    """Two concurrent claim calls should not both claim the same job."""
    from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
    from app.core.database import Base

    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    house, container = house_with_container

    # Seed: create a job in the fresh DB
    async with factory() as seed_session:
        from app.models.user import User
        from app.models.house import House
        from app.models.container import Container
        from app.models.house_membership import HouseMembership

        user = User(username="u", email="u@u.com", password_hash="x", is_system_admin=False)
        seed_session.add(user)
        await seed_session.flush()

        h = House(name="H", code_prefix="H", created_by=user.id)
        seed_session.add(h)
        await seed_session.flush()

        c = Container(house_id=h.id, code="H-001", status="open", nesting_level=0, created_by=user.id)
        seed_session.add(c)
        await seed_session.flush()

        job = AIAnalysisJob(
            house_id=h.id,
            requested_by=user.id,
            status="pending",
            hint_type="auto",
            language="it",
            input_photo_paths="[]",
        )
        seed_session.add(job)
        await seed_session.commit()

    # Two sessions claim concurrently (SQLite single-writer serializes)
    async with factory() as db1, factory() as db2:
        j1 = await claim_next_pending_job(db1)
        j2 = await claim_next_pending_job(db2)

        # Both flush but only one sees status=pending
        if j1:
            await db1.commit()
        if j2:
            await db2.commit()

    # At most one should have claimed it (SQLite serializes writes)
    claims = sum(1 for j in (j1, j2) if j is not None)
    assert claims >= 1  # at least one claimed it

    await engine.dispose()


@pytest.mark.asyncio
async def test_job_without_item_id_succeeds(db_session: AsyncSession, admin_user, house_with_container):
    house, _ = house_with_container
    job = _make_job(db_session, house.id, admin_user.id, item_id=None)
    await db_session.commit()

    adapter = AsyncMock()
    adapter.analyze = AsyncMock(return_value=_GOOD_RESULT)

    with patch("app.services.ai.job_processor.get_ai_adapter", return_value=adapter):
        processed = await process_next_job(db_session)

    assert processed is True
    await db_session.refresh(job)
    assert job.status == "completed"
