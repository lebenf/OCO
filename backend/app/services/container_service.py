# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import io
import math
import textwrap
import uuid
from datetime import datetime, timezone
from pathlib import Path

import qrcode
from fastapi import HTTPException, UploadFile
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.container import Container
from app.models.container_photo import ContainerPhoto
from app.models.house import House
from app.models.item import Item
from app.models.location import Location
from app.schemas.container import (
    ContainerClose,
    ContainerCreate,
    ContainerDetail,
    ContainerMini,
    ContainerSummary,
    ContainerUpdate,
    ItemSummaryOut,
    LocationMini,
    PhotoOut,
    UserMini,
)
from app.schemas.pagination import Page


MAX_NESTING_LEVEL = 2


async def generate_container_code(house: House) -> str:
    house.container_sequence += 1
    return f"{house.code_prefix}-{house.container_sequence:03d}"


def generate_label_sheet_pdf(code: str, url: str, count: int, columns: int) -> bytes:
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    qr_buf = io.BytesIO()
    qr_img.save(qr_buf, format="PNG")
    qr_buf.seek(0)
    qr_reader = ImageReader(qr_buf)

    page_width, page_height = A4
    margin = 10 * mm
    padding = 4 * mm
    rows = math.ceil(count / columns)

    cell_width = (page_width - 2 * margin) / columns
    cell_height = (page_height - 2 * margin) / rows
    qr_size = max(min(cell_width, cell_height - 8 * mm) - 2 * padding, 10 * mm)

    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)

    for i in range(count):
        row, col = divmod(i, columns)
        x0 = margin + col * cell_width
        y0 = page_height - margin - (row + 1) * cell_height

        pdf.setDash(2, 2)
        pdf.setStrokeColorRGB(0.7, 0.7, 0.7)
        pdf.rect(x0, y0, cell_width, cell_height)
        pdf.setDash()

        qr_x = x0 + (cell_width - qr_size) / 2
        qr_y = y0 + cell_height - padding - qr_size
        pdf.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)

        pdf.setFont("Helvetica-Bold", 12)
        pdf.setFillColorRGB(0, 0, 0)
        pdf.drawCentredString(x0 + cell_width / 2, y0 + padding + 2, code)

    pdf.save()
    return buf.getvalue()


def generate_thermal_label_image(code: str, description: str | None, url: str, width: int = 576) -> bytes:
    """Single PNG label: QR code + container code + description, for thermal label printers."""
    qr = qrcode.QRCode(border=1)
    qr.add_data(url)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("L")

    margin = width // 24
    qr_size = width - 2 * margin
    qr_img = qr_img.resize((qr_size, qr_size), Image.NEAREST)

    code_font = ImageFont.load_default(size=max(20, width // 14))
    desc_font = ImageFont.load_default(size=max(14, width // 22))
    line_gap = max(4, width // 96)

    desc_lines = textwrap.wrap(description, width=28) if description else []

    measurer = ImageDraw.Draw(Image.new("L", (1, 1)))
    code_bbox = measurer.textbbox((0, 0), code, font=code_font)
    code_h = code_bbox[3] - code_bbox[1]
    desc_line_heights = [
        measurer.textbbox((0, 0), line, font=desc_font)[3] - measurer.textbbox((0, 0), line, font=desc_font)[1]
        for line in desc_lines
    ]

    total_height = (
        margin + qr_size + line_gap * 2 + code_h
        + sum(h + line_gap for h in desc_line_heights)
        + margin
    )

    img = Image.new("L", (width, int(total_height)), 255)
    img.paste(qr_img, (margin, margin))
    draw = ImageDraw.Draw(img)

    y = margin + qr_size + line_gap * 2
    draw.text((width / 2, y), code, font=code_font, fill=0, anchor="ma")
    y += code_h + line_gap

    for line, h in zip(desc_lines, desc_line_heights):
        draw.text((width / 2, y), line, font=desc_font, fill=0, anchor="ma")
        y += h + line_gap

    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="PNG")
    return buf.getvalue()


async def get_container_or_404(container_id: str, house_id: str, db: AsyncSession) -> Container:
    container = await db.get(Container, container_id)
    if not container or container.house_id != house_id:
        raise HTTPException(status_code=404, detail={"detail": "Container not found", "code": "NOT_FOUND"})
    return container


def _photo_url(file_path: str) -> str:
    return f"/media/{file_path}"


async def _build_location_mini(location_id: str | None, db: AsyncSession) -> LocationMini | None:
    if not location_id:
        return None
    loc = await db.get(Location, location_id)
    if not loc:
        return None
    house = await db.get(House, loc.house_id)
    return LocationMini(
        id=loc.id,
        name=loc.name,
        house_id=loc.house_id,
        house_name=house.name if house else "",
    )


async def _build_summary(container: Container, db: AsyncSession) -> ContainerSummary:
    item_count = (
        await db.execute(
            select(func.count()).select_from(Item).where(Item.container_id == container.id)
        )
    ).scalar_one()

    children_count = (
        await db.execute(
            select(func.count()).select_from(Container).where(Container.parent_id == container.id)
        )
    ).scalar_one()

    cover_url = None
    if container.cover_photo_id:
        photo = await db.get(ContainerPhoto, container.cover_photo_id)
        if photo:
            cover_url = _photo_url(photo.file_path)

    current_location = await _build_location_mini(container.current_location_id, db)
    destination_location = await _build_location_mini(container.destination_location_id, db)

    return ContainerSummary(
        id=container.id,
        code=container.code,
        status=container.status,
        description=container.description,
        current_location=current_location,
        destination_location=destination_location,
        item_count=item_count,
        volume_liters=float(container.volume_liters) if container.volume_liters else None,
        cover_photo_url=cover_url,
        nesting_level=container.nesting_level,
        children_count=children_count,
    )


async def _calculate_total_volume(container: Container, db: AsyncSession) -> float:
    total = float(container.volume_liters or 0)
    children = (
        await db.execute(select(Container).where(Container.parent_id == container.id))
    ).scalars().all()
    for child in children:
        total += float(child.volume_liters or 0)
        grandchildren = (
            await db.execute(select(Container).where(Container.parent_id == child.id))
        ).scalars().all()
        for gc in grandchildren:
            total += float(gc.volume_liters or 0)
    return total


async def list_containers(
    house_id: str,
    db: AsyncSession,
    *,
    status_filter: str | None,
    destination_location_id: str | None,
    destination_house_id: str | None,
    current_location_id: str | None,
    parent_id: str | None,
    search: str | None,
    page: int,
    size: int,
) -> Page[ContainerSummary]:
    q = select(Container).where(Container.house_id == house_id)
    if status_filter:
        q = q.where(Container.status == status_filter)
    if destination_location_id:
        q = q.where(Container.destination_location_id == destination_location_id)
    if current_location_id:
        q = q.where(Container.current_location_id == current_location_id)
    if parent_id:
        q = q.where(Container.parent_id == parent_id)
    if destination_house_id:
        # Filter containers whose destination_location belongs to the given house
        dest_location_ids = (
            await db.execute(
                select(Location.id).where(Location.house_id == destination_house_id)
            )
        ).scalars().all()
        q = q.where(Container.destination_location_id.in_(dest_location_ids))
    if search:
        q = q.where(Container.code.ilike(f"%{search}%") | Container.description.ilike(f"%{search}%"))

    total = (await db.execute(select(func.count()).select_from(q.subquery()))).scalar_one()
    rows = (await db.execute(q.offset((page - 1) * size).limit(size))).scalars().all()
    items = [await _build_summary(c, db) for c in rows]
    return Page(items=items, total=total, page=page, pages=max(1, math.ceil(total / size)))


async def create_container(
    house: House,
    data: ContainerCreate,
    created_by: str,
    db: AsyncSession,
) -> Container:
    nesting_level = 0
    if data.parent_id:
        parent = await db.get(Container, data.parent_id)
        if not parent or parent.house_id != house.id:
            raise HTTPException(status_code=404, detail={"detail": "Parent container not found", "code": "NOT_FOUND"})
        if parent.nesting_level >= MAX_NESTING_LEVEL:
            raise HTTPException(
                status_code=400,
                detail={"detail": f"Max nesting depth ({MAX_NESTING_LEVEL}) reached", "code": "MAX_NESTING_DEPTH"},
            )
        nesting_level = parent.nesting_level + 1

    volume = None
    if data.width_cm and data.depth_cm and data.height_cm:
        volume = data.width_cm * data.depth_cm * data.height_cm / 1000

    code = await generate_container_code(house)

    container = Container(
        house_id=house.id,
        code=code,
        parent_id=data.parent_id,
        nesting_level=nesting_level,
        status="open",
        destination_location_id=data.destination_location_id,
        current_location_id=data.current_location_id,
        width_cm=data.width_cm,
        depth_cm=data.depth_cm,
        height_cm=data.height_cm,
        volume_liters=volume,
        description=data.description,
        created_by=created_by,
    )
    db.add(container)
    await db.commit()
    await db.refresh(container)
    return container


async def update_container(container: Container, data: ContainerUpdate, db: AsyncSession) -> Container:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(container, field, value)
    if data.width_cm is not None and data.depth_cm is not None and data.height_cm is not None:
        container.volume_liters = data.width_cm * data.depth_cm * data.height_cm / 1000
    await db.commit()
    await db.refresh(container)
    return container


async def _collect_descendant_ids(container_id: str, db: AsyncSession) -> set[str]:
    ids: set[str] = set()
    frontier = [container_id]
    while frontier:
        rows = (
            await db.execute(select(Container.id).where(Container.parent_id.in_(frontier)))
        ).scalars().all()
        frontier = [r for r in rows if r not in ids]
        ids.update(frontier)
    return ids


async def _subtree_depth(container_id: str, db: AsyncSession) -> int:
    children = (
        await db.execute(select(Container.id).where(Container.parent_id == container_id))
    ).scalars().all()
    if not children:
        return 0
    return 1 + max([await _subtree_depth(c, db) for c in children])


async def move_container(container: Container, new_parent_id: str | None, db: AsyncSession) -> Container:
    if new_parent_id == container.parent_id:
        return container

    new_level = 0
    descendant_ids = await _collect_descendant_ids(container.id, db)

    if new_parent_id:
        if new_parent_id == container.id or new_parent_id in descendant_ids:
            raise HTTPException(
                status_code=400,
                detail={"detail": "Cannot move a container into itself or one of its own contents", "code": "INVALID_PARENT"},
            )
        new_parent = await db.get(Container, new_parent_id)
        if not new_parent or new_parent.house_id != container.house_id:
            raise HTTPException(status_code=404, detail={"detail": "Parent container not found", "code": "NOT_FOUND"})
        new_level = new_parent.nesting_level + 1

    subtree_depth = await _subtree_depth(container.id, db)
    if new_level + subtree_depth > MAX_NESTING_LEVEL:
        raise HTTPException(
            status_code=400,
            detail={"detail": f"Max nesting depth ({MAX_NESTING_LEVEL}) reached", "code": "MAX_NESTING_DEPTH"},
        )

    level_diff = new_level - container.nesting_level
    container.parent_id = new_parent_id
    container.nesting_level = new_level

    if level_diff and descendant_ids:
        descendants = (
            await db.execute(select(Container).where(Container.id.in_(descendant_ids)))
        ).scalars().all()
        for descendant in descendants:
            descendant.nesting_level += level_diff

    await db.commit()
    await db.refresh(container)
    return container


async def close_container(container: Container, data: ContainerClose, db: AsyncSession) -> Container:
    if container.status not in ("open", "closed"):
        raise HTTPException(
            status_code=400,
            detail={"detail": f"Cannot close container in status '{container.status}'", "code": "INVALID_STATUS"},
        )
    container.status = "closed"
    container.closed_at = datetime.now(timezone.utc)
    if data.destination_location_id is not None:
        container.destination_location_id = data.destination_location_id
    if data.current_location_id is not None:
        container.current_location_id = data.current_location_id
    await db.commit()
    await db.refresh(container)
    return container


async def seal_container(container: Container, db: AsyncSession) -> Container:
    if container.status != "closed":
        raise HTTPException(
            status_code=400,
            detail={"detail": "Container must be closed before sealing", "code": "INVALID_STATUS"},
        )
    container.status = "sealed"
    await db.commit()
    await db.refresh(container)
    return container


async def save_photo(
    file: UploadFile,
    house_id: str,
    container_id: str,
    phase: str | None,
    db: AsyncSession,
) -> ContainerPhoto:
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
    rel_dir = Path(house_id) / "containers" / container_id
    abs_dir = Path(settings.STORAGE_PATH) / rel_dir
    abs_dir.mkdir(parents=True, exist_ok=True)

    filename = f"{photo_uuid}.jpg"
    abs_path = abs_dir / filename
    img.save(str(abs_path), "JPEG", quality=85)

    rel_path = str(rel_dir / filename)
    photo = ContainerPhoto(
        container_id=container_id,
        file_path=rel_path,
        original_filename=file.filename,
        mime_type="image/jpeg",
        file_size_bytes=abs_path.stat().st_size,
        phase=phase,
    )
    db.add(photo)
    await db.flush()

    container = await db.get(Container, container_id)
    if container and not container.cover_photo_id:
        container.cover_photo_id = photo.id

    await db.commit()
    await db.refresh(photo)
    return photo


async def delete_photo(photo: ContainerPhoto, db: AsyncSession) -> None:
    container = await db.get(Container, photo.container_id)

    try:
        Path(settings.STORAGE_PATH, photo.file_path).unlink(missing_ok=True)
    except Exception:
        pass

    if container and container.cover_photo_id == photo.id:
        container.cover_photo_id = None

    await db.delete(photo)
    await db.commit()


async def delete_container_with_files(container: Container, db: AsyncSession) -> None:
    """Delete a container, its items (DB cascade) and every photo file involved.

    Both the container's own photos and those of the items it holds, since the
    cascade removes the rows and would otherwise orphan the files on disk.
    """
    from app.services.item_service import delete_item_files

    storage = Path(settings.STORAGE_PATH)

    items = (await db.execute(
        select(Item).where(Item.container_id == container.id)
    )).scalars().all()
    for item in items:
        await delete_item_files(item, db)

    photos = (await db.execute(
        select(ContainerPhoto).where(ContainerPhoto.container_id == container.id)
    )).scalars().all()
    for photo in photos:
        (storage / photo.file_path).unlink(missing_ok=True)

    container_dir = storage / container.house_id / "containers" / container.id
    try:
        container_dir.rmdir()
    except OSError:
        pass

    await db.delete(container)
    await db.commit()


async def get_container_detail(container: Container, db: AsyncSession) -> ContainerDetail:
    summary = await _build_summary(container, db)

    photos_rows = (
        await db.execute(
            select(ContainerPhoto)
            .where(ContainerPhoto.container_id == container.id)
            .order_by(ContainerPhoto.sort_order)
        )
    ).scalars().all()
    photos = [PhotoOut(id=p.id, url=_photo_url(p.file_path), phase=p.phase, sort_order=p.sort_order) for p in photos_rows]

    items_rows = (
        await db.execute(select(Item).where(Item.container_id == container.id))
    ).scalars().all()
    items = [ItemSummaryOut(id=i.id, name=i.name, status=i.status, item_type=i.item_type) for i in items_rows]

    children_rows = (
        await db.execute(select(Container).where(Container.parent_id == container.id))
    ).scalars().all()
    children = [await _build_summary(c, db) for c in children_rows]

    parent = None
    if container.parent_id:
        p = await db.get(Container, container.parent_id)
        if p:
            parent = ContainerMini(id=p.id, code=p.code, status=p.status)

    volume_calculated = await _calculate_total_volume(container, db)

    from app.models.user import User
    creator = await db.get(User, container.created_by)
    created_by = UserMini(id=creator.id, username=creator.username) if creator else UserMini(id="", username="unknown")

    return ContainerDetail(
        **summary.model_dump(),
        width_cm=float(container.width_cm) if container.width_cm else None,
        depth_cm=float(container.depth_cm) if container.depth_cm else None,
        height_cm=float(container.height_cm) if container.height_cm else None,
        photos=photos,
        items=items,
        children=children,
        parent=parent,
        volume_calculated=volume_calculated,
        created_by=created_by,
        created_at=container.created_at,
        updated_at=container.updated_at,
    )
