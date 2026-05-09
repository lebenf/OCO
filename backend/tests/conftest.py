# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

import app.models  # noqa: F401 — register all models before Base.metadata.create_all
from app.core.database import Base, get_db
from app.core.limiter import limiter
from app.core.security import hash_password
from app.main import app
from app.models.user import User

# Disable rate limiting in tests — all requests share the same ASGI client IP.
limiter.enabled = False

TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        username="admin",
        email="admin@example.com",
        password_hash=hash_password("password123"),
        is_system_admin=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def regular_user(db_session: AsyncSession) -> User:
    user = User(
        username="member",
        email="member@example.com",
        password_hash=hash_password("password123"),
        is_system_admin=False,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
async def auth_client(client: AsyncClient, admin_user: User):
    """Client with valid auth cookies from admin login."""
    resp = await client.post("/api/auth/login", json={"username": "admin", "password": "password123"})
    assert resp.status_code == 200
    return client
