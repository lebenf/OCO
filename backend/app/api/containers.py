# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import io

import qrcode
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, get_house_member
from app.models.container import Container
from app.models.container_photo import ContainerPhoto
from app.models.house import House
from app.models.user import User
from app.schemas.container import (
    ContainerClose,
    ContainerCreate,
    ContainerDetail,
    ContainerSummary,
    ContainerUpdate,
    PhotoOut,
)
from app.schemas.pagination import Page
from app.services.container_service import (
    close_container,
    create_container,
    delete_photo,
    get_container_detail,
    get_container_or_404,
    list_containers,
    save_photo,
    seal_container,
    update_container,
    _photo_url,
)

router = APIRouter(prefix="/houses", tags=["containers"])


@router.get("/{house_id}/containers", response_model=Page[ContainerSummary])
async def list_containers_endpoint(
    house: House = Depends(get_house_member),
    status_filter: str | None = Query(None, alias="status"),
    destination_location_id: str | None = Query(None),
    destination_house_id: str | None = Query(None),
    current_location_id: str | None = Query(None),
    parent_id: str | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> Page[ContainerSummary]:
    return await list_containers(
        house.id, db,
        status_filter=status_filter,
        destination_location_id=destination_location_id,
        destination_house_id=destination_house_id,
        current_location_id=current_location_id,
        parent_id=parent_id,
        search=search,
        page=page,
        size=size,
    )


@router.post("/{house_id}/containers", response_model=ContainerDetail, status_code=status.HTTP_201_CREATED)
async def create_container_endpoint(
    body: ContainerCreate,
    house: House = Depends(get_house_member),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ContainerDetail:
    container = await create_container(house, body, created_by=current_user.id, db=db)
    return await get_container_detail(container, db)


@router.get("/{house_id}/containers/{code_or_id}", response_model=ContainerDetail)
async def get_container_by_code_or_id(
    code_or_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ContainerDetail:
    from sqlalchemy import or_
    result = await db.execute(
        select(Container).where(
            Container.house_id == house.id,
            or_(Container.id == code_or_id, Container.code == code_or_id),
        )
    )
    container = result.scalar_one_or_none()
    if not container:
        raise HTTPException(status_code=404, detail={"detail": "Container not found", "code": "NOT_FOUND"})
    return await get_container_detail(container, db)


@router.put("/{house_id}/containers/{container_id}", response_model=ContainerDetail)
async def update_container_endpoint(
    container_id: str,
    body: ContainerUpdate,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ContainerDetail:
    container = await get_container_or_404(container_id, house.id, db)
    container = await update_container(container, body, db)
    return await get_container_detail(container, db)


@router.post("/{house_id}/containers/{container_id}/close", response_model=ContainerDetail)
async def close_container_endpoint(
    container_id: str,
    body: ContainerClose,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ContainerDetail:
    container = await get_container_or_404(container_id, house.id, db)
    container = await close_container(container, body, db)
    return await get_container_detail(container, db)


@router.post("/{house_id}/containers/{container_id}/seal", response_model=ContainerDetail)
async def seal_container_endpoint(
    container_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> ContainerDetail:
    container = await get_container_or_404(container_id, house.id, db)
    container = await seal_container(container, db)
    return await get_container_detail(container, db)


@router.post("/{house_id}/containers/{container_id}/photos", response_model=PhotoOut, status_code=status.HTTP_201_CREATED)
async def upload_photo(
    container_id: str,
    file: UploadFile = File(...),
    phase: str | None = Form(None),
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> PhotoOut:
    await get_container_or_404(container_id, house.id, db)
    photo = await save_photo(file, house.id, container_id, phase, db)
    return PhotoOut(id=photo.id, url=_photo_url(photo.file_path), phase=photo.phase, sort_order=photo.sort_order)


@router.delete("/{house_id}/containers/{container_id}/photos/{photo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_photo_endpoint(
    container_id: str,
    photo_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> None:
    await get_container_or_404(container_id, house.id, db)
    photo = await db.get(ContainerPhoto, photo_id)
    if not photo or photo.container_id != container_id:
        raise HTTPException(status_code=404, detail={"detail": "Photo not found", "code": "NOT_FOUND"})
    await delete_photo(photo, db)


@router.get("/{house_id}/containers/{container_id}/qr")
async def get_qr_code(
    container_id: str,
    house: House = Depends(get_house_member),
    size: int = Query(300, ge=100, le=1000),
    db: AsyncSession = Depends(get_db),
) -> Response:
    container = await get_container_or_404(container_id, house.id, db)
    url = f"{settings.APP_HOST}/containers/{container.code}"

    box_size = max(1, size // 37)
    qr = qrcode.QRCode(version=1, box_size=box_size, border=4)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return Response(content=buf.getvalue(), media_type="image/png")
