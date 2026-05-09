# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_house_member
from app.models.category import Category
from app.models.house import House
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/houses", tags=["categories"])


@router.get("/{house_id}/categories", response_model=list[CategoryOut])
async def list_categories(
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> list[CategoryOut]:
    from sqlalchemy import or_
    rows = (await db.execute(
        select(Category).where(
            or_(Category.house_id == house.id, Category.is_system == True)
        ).order_by(Category.name)
    )).scalars().all()
    return [CategoryOut(id=c.id, name=c.name, icon=c.icon, parent_id=c.parent_id, is_system=c.is_system, house_id=c.house_id) for c in rows]


@router.post("/{house_id}/categories", response_model=CategoryOut, status_code=status.HTTP_201_CREATED)
async def create_category(
    body: CategoryCreate,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> CategoryOut:
    cat = Category(house_id=house.id, name=body.name, icon=body.icon, parent_id=body.parent_id)
    db.add(cat)
    await db.commit()
    await db.refresh(cat)
    return CategoryOut(id=cat.id, name=cat.name, icon=cat.icon, parent_id=cat.parent_id, is_system=cat.is_system, house_id=cat.house_id)


@router.put("/{house_id}/categories/{category_id}", response_model=CategoryOut)
async def update_category(
    category_id: str,
    body: CategoryUpdate,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> CategoryOut:
    cat = await db.get(Category, category_id)
    if not cat or (cat.house_id != house.id and not cat.is_system):
        raise HTTPException(status_code=404, detail={"detail": "Category not found", "code": "NOT_FOUND"})
    if body.name is not None:
        cat.name = body.name
    if body.icon is not None:
        cat.icon = body.icon
    if body.parent_id is not None:
        cat.parent_id = body.parent_id
    await db.commit()
    await db.refresh(cat)
    return CategoryOut(id=cat.id, name=cat.name, icon=cat.icon, parent_id=cat.parent_id, is_system=cat.is_system, house_id=cat.house_id)


@router.delete("/{house_id}/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> None:
    cat = await db.get(Category, category_id)
    if not cat or cat.house_id != house.id:
        raise HTTPException(status_code=404, detail={"detail": "Category not found", "code": "NOT_FOUND"})
    if cat.is_system:
        raise HTTPException(status_code=400, detail={"detail": "Cannot delete system category", "code": "SYSTEM_CATEGORY"})
    await db.delete(cat)
    await db.commit()
