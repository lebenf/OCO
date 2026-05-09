# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from unittest.mock import patch
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.core.database import Base
import app.models  # noqa: F401
from app.models.user import User
from app.core.init_db import init_db


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.mark.asyncio
async def test_init_db_creates_admin():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    with (
        patch("app.core.init_db.engine", engine),
        patch("app.core.init_db.AsyncSessionLocal", session_factory),
    ):
        await init_db()
        await init_db()  # idempotent — second call does not duplicate

    async with session_factory() as session:
        result = await session.execute(select(User).where(User.is_system_admin == True))  # noqa: E712
        admins = result.scalars().all()

    assert len(admins) == 1
    assert admins[0].username == "admin"
    assert admins[0].is_system_admin is True

    await engine.dispose()
