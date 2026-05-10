# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import asyncio
import json
import logging
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_analysis_job import AIAnalysisJob
from app.models.item import Item
from app.models.item_photo import ItemPhoto
from app.services.ai.base import AIAnalysisResult
from app.services.ai.factory import get_ai_adapter

logger = logging.getLogger(__name__)


async def claim_next_pending_job(db: AsyncSession) -> AIAnalysisJob | None:
    is_pg = settings.DATABASE_URL.startswith("postgresql")
    stmt = (
        select(AIAnalysisJob)
        .where(AIAnalysisJob.status == "pending")
        .order_by(AIAnalysisJob.created_at)
        .limit(1)
    )
    if is_pg:
        stmt = stmt.with_for_update(skip_locked=True)

    result = await db.execute(stmt)
    job = result.scalar_one_or_none()
    if job:
        job.status = "processing"
        job.started_at = datetime.now(timezone.utc)
        await db.flush()
    return job


def _apply_result_to_item(item: Item, result: AIAnalysisResult, provider: str) -> None:
    item.name = result.name
    item.description = result.description or None
    item.item_type = result.item_type
    item.brand = result.brand
    item.model = result.model
    item.author = result.author
    item.title = result.title
    item.color = result.color
    item.quantity = result.quantity
    item.tags = json.dumps(result.tags) if result.tags else None
    item.ai_generated = True
    item.ai_confidence = result.confidence
    item.ai_provider = provider
    item.ai_result_raw = json.dumps({
        "name": result.name,
        "description": result.description,
        "item_type": result.item_type,
        "brand": result.brand,
        "model": result.model,
        "author": result.author,
        "title": result.title,
        "color": result.color,
        "quantity": result.quantity,
        "tags": result.tags,
        "confidence": result.confidence,
    })
    item.status = "draft_ai_done"
    item.ai_error = None


async def _promote_temp_photos(item: Item, photo_paths: list[str], db: AsyncSession) -> None:
    storage = Path(settings.STORAGE_PATH)
    existing = (await db.execute(
        select(func.count()).select_from(ItemPhoto).where(ItemPhoto.item_id == item.id)
    )).scalar_one()

    for i, rel_temp in enumerate(photo_paths):
        src = storage / rel_temp
        if not src.exists():
            continue
        dest_dir = storage / item.house_id / "items" / item.id
        dest_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{uuid.uuid4()}.jpg"
        dest = dest_dir / filename
        shutil.move(str(src), str(dest))
        rel_dest = str(Path(item.house_id) / "items" / item.id / filename)
        photo = ItemPhoto(
            item_id=item.id,
            file_path=rel_dest,
            mime_type="image/jpeg",
            file_size_bytes=dest.stat().st_size,
            sort_order=existing + i,
            is_primary=(existing + i == 0),
        )
        db.add(photo)


async def process_next_job(db: AsyncSession) -> bool:
    job = await claim_next_pending_job(db)
    if not job:
        return False

    start_ts = datetime.now(timezone.utc)
    try:
        photo_paths: list[str] = json.loads(job.input_photo_paths or "[]")
        adapter = get_ai_adapter()
        timeout = (
            settings.OLLAMA_TIMEOUT_SECONDS
            if settings.AI_PROVIDER == "ollama"
            else settings.AI_TIMEOUT_SECONDS
        )
        result: AIAnalysisResult = await asyncio.wait_for(
            adapter.analyze(photo_paths, job.hint_type or "auto", job.language),
            timeout=timeout,
        )

        if job.item_id:
            item = await db.get(Item, job.item_id)
            if item:
                _apply_result_to_item(item, result, settings.AI_PROVIDER)
                await _promote_temp_photos(item, photo_paths, db)

        job.status = "completed"
        job.parsed_result = json.dumps({
            "name": result.name,
            "description": result.description,
            "item_type": result.item_type,
            "brand": result.brand,
            "model": result.model,
            "confidence": result.confidence,
        })
        job.completed_at = datetime.now(timezone.utc)
        elapsed = (datetime.now(timezone.utc) - start_ts).total_seconds()
        job.duration_ms = int(elapsed * 1000)

    except asyncio.TimeoutError:
        logger.warning("AI job %s timed out", job.id)
        job.status = "failed"
        job.error_message = "timeout"
        job.completed_at = datetime.now(timezone.utc)
        if job.item_id:
            item = await db.get(Item, job.item_id)
            if item:
                item.status = "draft_ai_failed"
                item.ai_error = "timeout"

    except Exception as exc:
        logger.error("AI job %s failed: %s", job.id, exc)
        job.status = "failed"
        job.error_message = str(exc)[:500]
        job.completed_at = datetime.now(timezone.utc)
        if job.item_id:
            item = await db.get(Item, job.item_id)
            if item:
                item.status = "draft_ai_failed"
                item.ai_error = str(exc)[:500]

    await db.commit()
    return True
