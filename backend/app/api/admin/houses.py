# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.house import House
from app.models.user import User
from app.schemas.house import HouseCreate, HouseOut, HouseUpdate, MembershipCreate, MemberOut
from app.schemas.pagination import Page
from app.services.house_service import (
    add_member,
    create_house,
    get_house_members,
    list_houses,
    remove_member,
    update_house,
)

router = APIRouter(prefix="/houses", tags=["admin-houses"])


@router.get("", response_model=Page[HouseOut])
async def admin_list_houses(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Page[HouseOut]:
    return await list_houses(db, page, size)


@router.post("", response_model=HouseOut, status_code=status.HTTP_201_CREATED)
async def admin_create_house(
    body: HouseCreate,
    current_user: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> HouseOut:
    house = await create_house(db, body, created_by=current_user.id)
    return HouseOut.model_validate(house)


@router.put("/{house_id}", response_model=HouseOut)
async def admin_update_house(
    house_id: str,
    body: HouseUpdate,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> HouseOut:
    house = await db.get(House, house_id)
    if not house:
        raise HTTPException(status_code=404, detail={"detail": "House not found", "code": "NOT_FOUND"})
    if house.is_disposal:
        raise HTTPException(
            status_code=400,
            detail={"detail": "Cannot modify the disposal house", "code": "DISPOSAL_HOUSE_IMMUTABLE"},
        )
    house = await update_house(db, house, body)
    return HouseOut.model_validate(house)


@router.get("/{house_id}/members", response_model=list[MemberOut])
async def admin_list_members(
    house_id: str,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> list[MemberOut]:
    house = await db.get(House, house_id)
    if not house:
        raise HTTPException(status_code=404, detail={"detail": "House not found", "code": "NOT_FOUND"})
    return await get_house_members(db, house_id)


@router.post("/{house_id}/members", response_model=MemberOut, status_code=status.HTTP_201_CREATED)
async def admin_add_member(
    house_id: str,
    body: MembershipCreate,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> MemberOut:
    house = await db.get(House, house_id)
    if not house:
        raise HTTPException(status_code=404, detail={"detail": "House not found", "code": "NOT_FOUND"})
    user = await db.get(User, body.user_id)
    if not user:
        raise HTTPException(status_code=404, detail={"detail": "User not found", "code": "NOT_FOUND"})
    return await add_member(db, house_id, body.user_id, body.role)


@router.delete("/{house_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def admin_remove_member(
    house_id: str,
    user_id: str,
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await remove_member(db, house_id, user_id)
