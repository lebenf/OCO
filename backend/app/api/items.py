# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_admin_user, get_current_user, get_house_member
from app.models.house import House
from app.models.user import User
from app.schemas.item import (
    ConfirmAllOut,
    InboxResponse,
    ItemBatchCreate,
    ItemConfirm,
    ItemCreate,
    ItemDetail,
    ItemPhotoOut,
    ItemSummary,
    ItemUpdate,
    RetryAIOut,
)
from app.schemas.pagination import Page
from app.services.container_service import get_container_or_404
from app.services.item_service import (
    confirm_all_container_items,
    confirm_item,
    create_draft_item,
    create_draft_items_batch,
    get_inbox,
    get_item_detail,
    get_item_or_404,
    list_items,
    retry_ai,
    save_item_photo,
    update_item,
    _photo_url,
)

router = APIRouter(prefix="/houses", tags=["items"])


@router.post(
    "/{house_id}/containers/{container_id}/items",
    response_model=ItemDetail,
    status_code=status.HTTP_201_CREATED,
)
async def create_item(
    container_id: str,
    body: ItemCreate,
    house: House = Depends(get_house_member),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ItemDetail:
    container = await get_container_or_404(container_id, house.id, db)
    item, _ = await create_draft_item(container, house.id, body, current_user.id, db)
    return await get_item_detail(item, db)


@router.post(
    "/{house_id}/containers/{container_id}/items/batch",
    response_model=list[ItemDetail],
    status_code=status.HTTP_201_CREATED,
)
async def create_items_batch(
    container_id: str,
    body: ItemBatchCreate,
    house: House = Depends(get_house_member),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ItemDetail]:
    container = await get_container_or_404(container_id, house.id, db)
    results = await create_draft_items_batch(container, house.id, body.items, current_user.id, db)
    return [await get_item_detail(item, db) for item, _ in results]


@router.get("/{house_id}/items", response_model=Page[ItemSummary])
async def search_items(
    house: House = Depends(get_house_member),
    status_filter: str | None = Query("confirmed", alias="status"),
    container_id: str | None = Query(None),
    category_id: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Page[ItemSummary]:
    return await list_items(
        house.id, db,
        status_filter=status_filter,
        container_id=container_id,
        category_id=category_id,
        search=search,
        page=page,
        size=size,
    )


@router.get("/{house_id}/inbox", response_model=InboxResponse)
async def get_inbox_endpoint(
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> InboxResponse:
    return await get_inbox(house.id, db)


@router.get("/{house_id}/items/{item_id}", response_model=ItemDetail)
async def get_item(
    item_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ItemDetail:
    item = await get_item_or_404(item_id, house.id, db)
    return await get_item_detail(item, db)


@router.put("/{house_id}/items/{item_id}", response_model=ItemDetail)
async def update_item_endpoint(
    item_id: str,
    body: ItemUpdate,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ItemDetail:
    item = await get_item_or_404(item_id, house.id, db)
    item = await update_item(item, body, house.id, db)
    return await get_item_detail(item, db)


@router.delete("/{house_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: str,
    house: House = Depends(get_house_member),
    _: User = Depends(get_admin_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    item = await get_item_or_404(item_id, house.id, db)
    await db.delete(item)
    await db.commit()


@router.put("/{house_id}/items/{item_id}/confirm", response_model=ItemDetail)
async def confirm_item_endpoint(
    item_id: str,
    body: ItemConfirm,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ItemDetail:
    item = await get_item_or_404(item_id, house.id, db)
    item = await confirm_item(item, body, house.id, db)
    return await get_item_detail(item, db)


@router.post("/{house_id}/items/{item_id}/retry-ai", response_model=RetryAIOut)
async def retry_ai_endpoint(
    item_id: str,
    house: House = Depends(get_house_member),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> RetryAIOut:
    item = await get_item_or_404(item_id, house.id, db)
    job = await retry_ai(item, current_user.id, db)
    return RetryAIOut(job_id=job.id)


@router.post("/{house_id}/containers/{container_id}/confirm-all", response_model=ConfirmAllOut)
async def confirm_all_endpoint(
    container_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ConfirmAllOut:
    container = await get_container_or_404(container_id, house.id, db)
    return await confirm_all_container_items(container, db)


@router.post(
    "/{house_id}/items/{item_id}/photos",
    response_model=ItemPhotoOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_item_photo(
    item_id: str,
    file: UploadFile = File(...),
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ItemPhotoOut:
    item = await get_item_or_404(item_id, house.id, db)
    photo = await save_item_photo(file, house.id, item.id, db)
    return ItemPhotoOut(id=photo.id, url=_photo_url(photo.file_path), is_primary=photo.is_primary, sort_order=photo.sort_order)
