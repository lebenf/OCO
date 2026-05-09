# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_house_member
from app.models.house import House
from app.models.user import User
from app.schemas.transfer import (
    AddContainersRequest,
    LocationSummaryOut,
    TransferCreate,
    TransferDetail,
    TransferPlanRequest,
    TransferPlanResponse,
    TransferSummary,
    TransferUpdate,
)
from app.services import transfer_service

router = APIRouter()


@router.get("/houses/{house_id}/transfers", response_model=list[TransferSummary])
async def list_transfers(
    status: str | None = Query(None),
    destination_location_id: str | None = Query(None),
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.list_transfers(house.id, db, status, destination_location_id)


@router.post("/houses/{house_id}/transfers", response_model=TransferDetail)
async def create_transfer(
    data: TransferCreate,
    house: House = Depends(get_house_member),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.create_transfer(house.id, current_user.id, data, db)


@router.post("/houses/{house_id}/transfers/plan", response_model=TransferPlanResponse)
async def plan_transfers(
    request: TransferPlanRequest,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.plan_transfers(house.id, request, db)


@router.get("/houses/{house_id}/transfers/{transfer_id}", response_model=TransferDetail)
async def get_transfer(
    transfer_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.get_transfer_detail(transfer_id, house.id, db)


@router.put("/houses/{house_id}/transfers/{transfer_id}", response_model=TransferDetail)
async def update_transfer(
    transfer_id: str,
    data: TransferUpdate,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.update_transfer(transfer_id, house.id, data, db)


@router.post("/houses/{house_id}/transfers/{transfer_id}/start", response_model=TransferDetail)
async def start_transfer(
    transfer_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.start_transfer(transfer_id, house.id, db)


@router.post("/houses/{house_id}/transfers/{transfer_id}/complete", response_model=TransferDetail)
async def complete_transfer(
    transfer_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.complete_transfer(transfer_id, house.id, db)


@router.post("/houses/{house_id}/transfers/{transfer_id}/containers", response_model=TransferDetail)
async def add_containers(
    transfer_id: str,
    body: AddContainersRequest,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.add_containers(transfer_id, house.id, body.container_ids, db)


@router.delete(
    "/houses/{house_id}/transfers/{transfer_id}/containers/{container_id}",
    response_model=TransferDetail,
)
async def remove_container(
    transfer_id: str,
    container_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.remove_container(transfer_id, container_id, house.id, db)


@router.get(
    "/houses/{house_id}/locations/{location_id}/summary",
    response_model=LocationSummaryOut,
)
async def location_summary(
    location_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    return await transfer_service.get_location_summary(location_id, house.id, db)
