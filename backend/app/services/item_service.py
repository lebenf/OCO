# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import io
import json
import math
import uuid
from datetime import datetime, timezone
from pathlib import Path

from fastapi import HTTPException, UploadFile
from PIL import Image
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.ai_analysis_job import AIAnalysisJob
from app.models.category import Category
from app.models.container import Container
from app.models.item import Item
from app.models.item_category import ItemCategory
from app.models.item_photo import ItemPhoto
from app.schemas.item import (
    CategoryMini,
    ConfirmAllOut,
    ContainerInboxGroup,
    DraftItemSummary,
    InboxResponse,
    ItemConfirm,
    ItemCreate,
    ItemDetail,
    ItemPhotoOut,
    ItemSummary,
    ItemUpdate,
)
from app.schemas.pagination import Page


def _photo_url(file_path: str) -> str:
    return f"/media/{file_path}"


def _temp_photo_path(photo_id: str) -> str:
    return str(Path("temp") / f"{photo_id}.jpg")


async def _get_or_create_category(name: str, house_id: str, db: AsyncSession) -> Category:
    result = await db.execute(
        select(Category).where(
            or_(
                (Category.house_id == house_id) & (Category.name == name),
                Category.is_system & (Category.name == name),
            )
        )
    )
    cat = result.scalar_one_or_none()
    if not cat:
        cat = Category(house_id=house_id, name=name)
        db.add(cat)
        await db.flush()
    return cat


async def _build_summary(item: Item, db: AsyncSession) -> ItemSummary:
    primary_photo = None
    photos = (await db.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id).order_by(ItemPhoto.sort_order)
    )).scalars().all()
    for p in photos:
        if p.is_primary:
            primary_photo = _photo_url(p.file_path)
            break
    if not primary_photo and photos:
        primary_photo = _photo_url(photos[0].file_path)

    cat_links = (await db.execute(
        select(ItemCategory).where(ItemCategory.item_id == item.id)
    )).scalars().all()
    categories: list[CategoryMini] = []
    for link in cat_links:
        cat = await db.get(Category, link.category_id)
        if cat:
            categories.append(CategoryMini(id=cat.id, name=cat.name, icon=cat.icon))

    return ItemSummary(
        id=item.id,
        name=item.name,
        status=item.status,
        item_type=item.item_type,
        brand=item.brand,
        color=item.color,
        quantity=item.quantity,
        ai_generated=item.ai_generated,
        container_id=item.container_id,
        primary_photo_url=primary_photo,
        categories=categories,
    )


async def get_item_detail(item: Item, db: AsyncSession) -> ItemDetail:
    summary = await _build_summary(item, db)
    photos_rows = (await db.execute(
        select(ItemPhoto).where(ItemPhoto.item_id == item.id).order_by(ItemPhoto.sort_order)
    )).scalars().all()
    photos = [ItemPhotoOut(id=p.id, url=_photo_url(p.file_path), is_primary=p.is_primary, sort_order=p.sort_order) for p in photos_rows]

    tags = json.loads(item.tags) if item.tags else []
    ai_conf = float(item.ai_confidence) if item.ai_confidence is not None else None

    return ItemDetail(
        **summary.model_dump(),
        description=item.description,
        model=item.model,
        author=item.author,
        title=item.title,
        ai_confidence=ai_conf,
        ai_provider=item.ai_provider,
        ai_error=item.ai_error,
        ai_result_raw=item.ai_result_raw,
        notes=item.notes,
        tags=tags,
        photos=photos,
        created_at=item.created_at,
        updated_at=item.updated_at,
    )


async def _enqueue_ai_job(
    item: Item,
    house_id: str,
    requested_by: str,
    hint_type: str,
    language: str,
    photo_ids: list[str],
    db: AsyncSession,
) -> AIAnalysisJob:
    photo_paths = [_temp_photo_path(pid) for pid in photo_ids]
    job = AIAnalysisJob(
        house_id=house_id,
        requested_by=requested_by,
        status="pending",
        hint_type=hint_type,
        language=language,
        item_id=item.id,
        input_photo_paths=json.dumps(photo_paths),
        provider=settings.AI_PROVIDER,
        model=settings.OLLAMA_MODEL if settings.AI_PROVIDER == "ollama" else None,
    )
    db.add(job)
    await db.flush()
    item.ai_job_id = job.id
    return job


async def create_draft_item(
    container: Container,
    house_id: str,
    data: ItemCreate,
    created_by: str,
    db: AsyncSession,
) -> tuple[Item, AIAnalysisJob]:
    item = Item(
        container_id=container.id,
        house_id=house_id,
        status="draft",
        item_type=data.item_type,
        name=data.name or "placeholder",
        created_by=created_by,
    )
    db.add(item)
    await db.flush()

    job = await _enqueue_ai_job(item, house_id, created_by, data.hint_type, data.language, data.photo_ids, db)
    await db.commit()
    await db.refresh(item)
    return item, job


async def create_draft_items_batch(
    container: Container,
    house_id: str,
    items_data: list[ItemCreate],
    created_by: str,
    db: AsyncSession,
) -> list[tuple[Item, AIAnalysisJob]]:
    results = []
    for data in items_data:
        item = Item(
            container_id=container.id,
            house_id=house_id,
            status="draft",
            item_type=data.item_type,
            name=data.name or "placeholder",
            created_by=created_by,
        )
        db.add(item)
        await db.flush()
        job = await _enqueue_ai_job(item, house_id, created_by, data.hint_type, data.language, data.photo_ids, db)
        results.append((item, job))
    await db.commit()
    for item, job in results:
        await db.refresh(item)
    return results


async def confirm_item(item: Item, data: ItemConfirm, house_id: str, db: AsyncSession) -> Item:
    item.name = data.name
    item.description = data.description
    item.brand = data.brand
    item.model = data.model
    item.author = data.author
    item.title = data.title
    item.color = data.color
    item.quantity = data.quantity
    item.item_type = data.item_type
    item.notes = data.notes
    item.tags = json.dumps(data.tags) if data.tags else None
    item.status = "confirmed"

    if data.category_ids is not None:
        existing = (await db.execute(
            select(ItemCategory).where(ItemCategory.item_id == item.id)
        )).scalars().all()
        for link in existing:
            await db.delete(link)
        await db.flush()
        for cat_id in data.category_ids:
            db.add(ItemCategory(item_id=item.id, category_id=cat_id))

    await db.commit()
    await db.refresh(item)
    return item


async def update_item(item: Item, data: ItemUpdate, house_id: str, db: AsyncSession) -> Item:
    if data.name is not None:
        item.name = data.name
    if data.description is not None:
        item.description = data.description
    if data.brand is not None:
        item.brand = data.brand
    if data.model is not None:
        item.model = data.model
    if data.author is not None:
        item.author = data.author
    if data.title is not None:
        item.title = data.title
    if data.color is not None:
        item.color = data.color
    if data.quantity is not None:
        item.quantity = data.quantity
    if data.item_type is not None:
        item.item_type = data.item_type
    if data.notes is not None:
        item.notes = data.notes
    if data.tags is not None:
        item.tags = json.dumps(data.tags)

    if data.category_ids is not None:
        existing = (await db.execute(
            select(ItemCategory).where(ItemCategory.item_id == item.id)
        )).scalars().all()
        for link in existing:
            await db.delete(link)
        await db.flush()
        for cat_id in data.category_ids:
            db.add(ItemCategory(item_id=item.id, category_id=cat_id))

    await db.commit()
    await db.refresh(item)
    return item


async def retry_ai(item: Item, requested_by: str, db: AsyncSession) -> AIAnalysisJob:
    if item.status not in ("draft_ai_failed",):
        raise HTTPException(
            status_code=400,
            detail={"detail": "Only failed items can be retried", "code": "INVALID_STATUS"},
        )
    old_job = await db.get(AIAnalysisJob, item.ai_job_id) if item.ai_job_id else None
    old_photo_paths: list[str] = json.loads(old_job.input_photo_paths or "[]") if old_job else []

    job = AIAnalysisJob(
        house_id=item.house_id,
        requested_by=requested_by,
        status="pending",
        hint_type=old_job.hint_type if old_job else "auto",
        language=old_job.language if old_job else "it",
        item_id=item.id,
        input_photo_paths=json.dumps(old_photo_paths),
        provider=settings.AI_PROVIDER,
        retry_count=(old_job.retry_count + 1) if old_job else 1,
    )
    db.add(job)
    await db.flush()

    item.status = "draft"
    item.ai_job_id = job.id
    item.ai_error = None

    await db.commit()
    await db.refresh(job)
    return job


async def confirm_all_container_items(container: Container, db: AsyncSession) -> ConfirmAllOut:
    items = (await db.execute(
        select(Item).where(Item.container_id == container.id)
    )).scalars().all()

    confirmed = skipped_failed = skipped_pending = 0
    for item in items:
        if item.status == "draft_ai_done":
            if item.ai_result_raw:
                raw = json.loads(item.ai_result_raw)
                item.name = raw.get("name", item.name)
            item.status = "confirmed"
            confirmed += 1
        elif item.status == "draft_ai_failed":
            skipped_failed += 1
        elif item.status == "draft":
            skipped_pending += 1

    await db.commit()
    return ConfirmAllOut(confirmed=confirmed, skipped_failed=skipped_failed, skipped_pending=skipped_pending)


async def save_item_photo(
    file: UploadFile,
    house_id: str,
    item_id: str,
    db: AsyncSession,
) -> ItemPhoto:
    content = await file.read()

    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail={"detail": f"File exceeds {settings.MAX_UPLOAD_SIZE_MB}MB limit", "code": "FILE_TOO_LARGE"},
        )

    try:
        img = Image.open(io.BytesIO(content)).convert("RGB")
    except Exception:
        raise HTTPException(status_code=400, detail={"detail": "Invalid image file", "code": "INVALID_IMAGE"})

    max_px = 1920
    if img.width > max_px or img.height > max_px:
        img.thumbnail((max_px, max_px), Image.LANCZOS)

    photo_uuid = str(uuid.uuid4())
    rel_dir = Path(house_id) / "items" / item_id
    abs_dir = Path(settings.STORAGE_PATH) / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{photo_uuid}.jpg"
    abs_path = abs_dir / filename
    img.save(str(abs_path), "JPEG", quality=85)

    existing_count = (await db.execute(
        select(func.count()).select_from(ItemPhoto).where(ItemPhoto.item_id == item_id)
    )).scalar_one()

    photo = ItemPhoto(
        item_id=item_id,
        file_path=str(rel_dir / filename),
        original_filename=file.filename,
        mime_type="image/jpeg",
        file_size_bytes=abs_path.stat().st_size,
        sort_order=existing_count,
        is_primary=(existing_count == 0),
    )
    db.add(photo)
    await db.commit()
    await db.refresh(photo)
    return photo


async def list_items(
    house_id: str,
    db: AsyncSession,
    *,
    status_filter: str | None = "confirmed",
    container_id: str | None = None,
    search: str | None = None,
    category_id: str | None = None,
    page: int = 1,
    size: int = 20,
) -> Page[ItemSummary]:
    q = select(Item).where(Item.house_id == house_id)
    if status_filter:
        q = q.where(Item.status == status_filter)
    if container_id:
        q = q.where(Item.container_id == container_id)
    if category_id:
        sub = select(ItemCategory.item_id).where(ItemCategory.category_id == category_id)
        q = q.where(Item.id.in_(sub))
    if search:
        q = q.where(
            Item.name.ilike(f"%{search}%")
            | Item.description.ilike(f"%{search}%")
            | Item.brand.ilike(f"%{search}%")
        )

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    rows = (await db.execute(q.offset((page - 1) * size).limit(size))).scalars().all()
    items = [await _build_summary(r, db) for r in rows]
    return Page(items=items, total=total, page=page, pages=max(1, math.ceil(total / size)))


async def get_inbox(house_id: str, db: AsyncSession) -> InboxResponse:
    draft_statuses = ["draft", "draft_ai_done", "draft_ai_failed"]
    rows = (await db.execute(
        select(Item).where(Item.house_id == house_id, Item.status.in_(draft_statuses))
        .order_by(Item.container_id, Item.created_at)
    )).scalars().all()

    by_container: dict[str, ContainerInboxGroup] = {}
    pending_ai = ready_for_review = failed = 0

    for item in rows:
        if item.status == "draft":
            pending_ai += 1
        elif item.status == "draft_ai_done":
            ready_for_review += 1
        elif item.status == "draft_ai_failed":
            failed += 1

        photos = (await db.execute(
            select(ItemPhoto).where(ItemPhoto.item_id == item.id, ItemPhoto.is_primary == True)
        )).scalars().all()
        primary_url = _photo_url(photos[0].file_path) if photos else None

        ai_result = json.loads(item.ai_result_raw) if item.ai_result_raw else None

        draft_item = DraftItemSummary(
            id=item.id,
            item_type=item.item_type,
            status=item.status,
            ai_error=item.ai_error,
            primary_photo_url=primary_url,
            ai_result=ai_result,
            created_at=item.created_at,
        )

        if item.container_id not in by_container:
            container = await db.get(Container, item.container_id)
            code = container.code if container else item.container_id
            by_container[item.container_id] = ContainerInboxGroup(
                container_id=item.container_id,
                container_code=code,
                items=[],
            )
        by_container[item.container_id].items.append(draft_item)

    return InboxResponse(
        total=len(rows),
        pending_ai=pending_ai,
        ready_for_review=ready_for_review,
        failed=failed,
        by_container=list(by_container.values()),
    )


async def get_item_or_404(item_id: str, house_id: str, db: AsyncSession) -> Item:
    item = await db.get(Item, item_id)
    if not item or item.house_id != house_id:
        raise HTTPException(status_code=404, detail={"detail": "Item not found", "code": "NOT_FOUND"})
    return item
