# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import asyncio
import logging

from app.core.database import get_db_session
from app.services.ai.job_processor import process_next_job

logger = logging.getLogger(__name__)


async def ai_worker_loop(interval_seconds: int = 5) -> None:
    logger.info("AI worker started (interval=%ds)", interval_seconds)
    while True:
        try:
            async with get_db_session() as db:
                processed = await process_next_job(db)
            if not processed:
                await asyncio.sleep(interval_seconds)
        except asyncio.CancelledError:
            logger.info("AI worker cancelled")
            return
        except Exception as exc:
            logger.error("AI worker error: %s", exc)
            await asyncio.sleep(interval_seconds)
