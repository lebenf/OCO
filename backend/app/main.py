# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import asyncio
import json
import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings
from app.core.limiter import limiter
from app.api.auth import router as auth_router
from app.api.admin.users import router as admin_users_router
from app.api.admin.houses import router as admin_houses_router
from app.api.admin.config import router as admin_config_router
from app.api.houses import router as houses_router
from app.api.containers import router as containers_router
from app.api.ai import router as ai_router
from app.api.items import router as items_router
from app.api.categories import router as categories_router
from app.api.transfers import router as transfers_router
from app.api.dashboard import router as dashboard_router


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        obj = {
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(record.created)),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        if record.exc_info:
            obj["exc"] = self.formatException(record.exc_info)
        return json.dumps(obj)


def _configure_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    handler = logging.StreamHandler()
    if settings.LOG_JSON:
        handler.setFormatter(_JsonFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)


_configure_logging()
logger = logging.getLogger(__name__)


class RequestLogMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.monotonic()
        response = await call_next(request)
        ms = int((time.monotonic() - start) * 1000)
        logger.info(
            "%s %s %s %dms",
            request.method,
            request.url.path,
            response.status_code,
            ms,
        )
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.services.ai.worker import ai_worker_loop
    Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
    worker_task = asyncio.create_task(ai_worker_loop())
    logger.info("OCO backend starting")
    yield
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass
    logger.info("OCO backend stopping")


app = FastAPI(
    title="OCO API",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestLogMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api")
app.include_router(admin_users_router, prefix="/api/admin")
app.include_router(admin_houses_router, prefix="/api/admin")
app.include_router(admin_config_router, prefix="/api/admin")
app.include_router(houses_router, prefix="/api")
app.include_router(containers_router, prefix="/api")
app.include_router(ai_router, prefix="/api")
app.include_router(items_router, prefix="/api")
app.include_router(categories_router, prefix="/api")
app.include_router(transfers_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

Path(settings.STORAGE_PATH).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.STORAGE_PATH), name="media")


@app.get("/health")
async def health(request: Request):
    from app.core.database import engine
    from app.core.ai_config import get_live_config
    from sqlalchemy import text

    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    cfg = get_live_config()
    ai_info: dict = {"provider": cfg["active_provider"]}

    return JSONResponse(
        status_code=200 if db_ok else 503,
        content={"status": "ok" if db_ok else "degraded", "db": db_ok, "ai": ai_info},
    )
