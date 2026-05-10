# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import asyncio
import logging

from app.core.config import settings
from app.core.database import get_db_session
from app.services.ai.job_processor import process_next_job

logger = logging.getLogger(__name__)


async def _worker_slot(slot_id: int, idle_interval: int) -> None:
    while True:
        try:
            async with get_db_session() as db:
                processed = await process_next_job(db)
            if not processed:
                await asyncio.sleep(idle_interval)
        except asyncio.CancelledError:
            return
        except Exception as exc:
            logger.error("AI worker slot %d error: %s", slot_id, exc)
            await asyncio.sleep(idle_interval)


async def ai_worker_loop(interval_seconds: int = 5) -> None:
    concurrency = settings.OLLAMA_CONCURRENCY if settings.AI_PROVIDER == "ollama" else 1
    logger.info("AI worker started (interval=%ds, concurrency=%d)", interval_seconds, concurrency)
    slots = [asyncio.create_task(_worker_slot(i, interval_seconds)) for i in range(concurrency)]
    try:
        await asyncio.gather(*slots)
    except asyncio.CancelledError:
        logger.info("AI worker cancelled")
        for slot in slots:
            slot.cancel()
        await asyncio.gather(*slots, return_exceptions=True)
