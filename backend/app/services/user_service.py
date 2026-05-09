# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import math

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.schemas.pagination import Page
from app.schemas.user import UserCreate, UserOut, UserUpdate


async def list_users(db: AsyncSession, page: int, size: int) -> Page[UserOut]:
    total = (await db.execute(select(func.count()).select_from(User))).scalar_one()
    rows = (await db.execute(select(User).offset((page - 1) * size).limit(size))).scalars().all()
    return Page(
        items=[UserOut.model_validate(u) for u in rows],
        total=total,
        page=page,
        pages=max(1, math.ceil(total / size)),
    )


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    user = User(
        username=data.username,
        email=data.email,
        password_hash=hash_password(data.password),
        is_system_admin=data.is_system_admin,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(db: AsyncSession, user: User) -> None:
    user.is_active = False
    await db.commit()


async def reset_password(db: AsyncSession, user: User, new_password: str) -> None:
    user.password_hash = hash_password(new_password)
    await db.commit()
