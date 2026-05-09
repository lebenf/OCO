# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.user import User
from app.schemas.pagination import Page
from app.schemas.user import ResetPasswordRequest, UserCreate, UserOut, UserUpdate
from app.services.user_service import (
    create_user,
    deactivate_user,
    list_users,
    reset_password,
    update_user,
)

router = APIRouter(prefix="/users", tags=["admin-users"])


@router.get("", response_model=Page[UserOut])
async def admin_list_users(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Page[UserOut]:
    return await list_users(db, page, size)


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def admin_create_user(
    body: UserCreate,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    user = await create_user(db, body)
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut)
async def admin_update_user(
    user_id: str,
    body: UserUpdate,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> UserOut:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"detail": "User not found", "code": "NOT_FOUND"})
    user = await update_user(db, user, body)
    return UserOut.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_delete_user(
    user_id: str,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"detail": "User not found", "code": "NOT_FOUND"})
    await deactivate_user(db, user)


@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def admin_reset_password(
    user_id: str,
    body: ResetPasswordRequest,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"detail": "User not found", "code": "NOT_FOUND"})
    await reset_password(db, user, body.new_password)
