# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.house_membership import HouseMembership
from app.schemas.auth import UserProfile, HouseMini


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    return result.scalar_one_or_none()


async def build_user_profile(db: AsyncSession, user_id: str) -> UserProfile:
    result = await db.execute(
        select(User)
        .options(
            selectinload(User.memberships).selectinload(HouseMembership.house)
        )
        .where(User.id == user_id)
    )
    user = result.scalar_one()
    houses = [
        HouseMini(id=m.house.id, name=m.house.name, role=m.role)
        for m in user.memberships
    ]
    return UserProfile(
        id=user.id,
        username=user.username,
        email=user.email,
        is_system_admin=user.is_system_admin,
        preferred_language=user.preferred_language,
        houses=houses,
    )
