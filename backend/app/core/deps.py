# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import Depends, HTTPException, Path, Request, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.user import User


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Not authenticated", "code": "NOT_AUTHENTICATED"},
        )
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            raise ValueError("wrong token type")
        user_id: str = payload["sub"]
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Invalid token", "code": "INVALID_TOKEN"},
        )

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "User not found or inactive", "code": "USER_INACTIVE"},
        )
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_system_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"detail": "Admin access required", "code": "FORBIDDEN"},
        )
    return current_user


async def get_house_and_membership(
    house_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> tuple[House, HouseMembership | None]:
    house = await db.get(House, house_id)
    if not house:
        raise HTTPException(status_code=404, detail={"detail": "House not found", "code": "NOT_FOUND"})

    if current_user.is_system_admin:
        return house, None

    membership = (
        await db.execute(
            select(HouseMembership).where(
                HouseMembership.house_id == house_id,
                HouseMembership.user_id == current_user.id,
            )
        )
    ).scalar_one_or_none()

    if not membership:
        raise HTTPException(status_code=403, detail={"detail": "Not a member", "code": "FORBIDDEN"})

    return house, membership


async def get_house_admin(
    house_and_membership: tuple[House, HouseMembership | None] = Depends(get_house_and_membership),
    current_user: User = Depends(get_current_user),
) -> House:
    house, membership = house_and_membership
    if not current_user.is_system_admin and (membership is None or membership.role != "admin"):
        raise HTTPException(status_code=403, detail={"detail": "House admin role required", "code": "FORBIDDEN"})
    return house


async def get_house_member(
    house_and_membership: tuple[House, HouseMembership | None] = Depends(get_house_and_membership),
) -> House:
    house, _ = house_and_membership
    return house
