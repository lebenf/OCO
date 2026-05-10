# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from datetime import datetime, timezone
from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.container import Container
from app.models.house import House
from app.models.location import Location
from app.models.transfer import Transfer
from app.models.transfer_container import TransferContainer
from app.schemas.container import ContainerSummary, LocationMini
from app.schemas.transfer import (
    AddContainersRequest,
    LocationSummaryOut,
    TransferCreate,
    TransferDetail,
    TransferPlanRequest,
    TransferPlanResponse,
    TransferSummary,
    TransferUpdate,
    TripPlan,
)
from app.services.container_service import _build_location_mini, _build_summary


def group_containers_ffd(
    containers: list[Container],
    vehicle_volume_liters: float,
) -> tuple[list[list[Container]], list[Container]]:
    """First Fit Decreasing bin packing. Returns (trips, unassigned_without_volume)."""
    with_volume = [c for c in containers if c.volume_liters and float(c.volume_liters) > 0]
    without_volume = [c for c in containers if not c.volume_liters or float(c.volume_liters) == 0]

    sorted_containers = sorted(with_volume, key=lambda c: float(c.volume_liters or 0), reverse=True)
    bins: list[tuple[float, list[Container]]] = []

    for container in sorted_containers:
        vol = float(container.volume_liters or 0)
        placed = False
        for i, (remaining, bin_containers) in enumerate(bins):
            if vol <= remaining:
                bins[i] = (remaining - vol, bin_containers + [container])
                placed = True
                break
        if not placed:
            bins.append((vehicle_volume_liters - vol, [container]))

    return [bin_containers for _, bin_containers in bins], without_volume


async def _get_transfer_or_404(transfer_id: str, house_id: str, db: AsyncSession) -> Transfer:
    transfer = await db.get(Transfer, transfer_id)
    if not transfer or transfer.house_id != house_id:
        raise HTTPException(status_code=404, detail={"detail": "Transfer not found", "code": "NOT_FOUND"})
    return transfer


async def _build_transfer_summary(transfer: Transfer, db: AsyncSession) -> TransferSummary:
    destination_location = await _build_location_mini(transfer.destination_location_id, db)

    links = (
        await db.execute(
            select(TransferContainer).where(TransferContainer.transfer_id == transfer.id)
        )
    ).scalars().all()

    total_volume = 0.0
    for link in links:
        c = await db.get(Container, link.container_id)
        if c and c.volume_liters:
            total_volume += float(c.volume_liters)

    return TransferSummary(
        id=transfer.id,
        name=transfer.name,
        status=transfer.status,
        destination_location=destination_location,
        scheduled_date=transfer.scheduled_date,
        vehicle_volume_liters=float(transfer.vehicle_volume_liters) if transfer.vehicle_volume_liters else None,
        container_count=len(links),
        total_volume_liters=total_volume,
    )


async def _build_transfer_detail(transfer: Transfer, db: AsyncSession) -> TransferDetail:
    summary = await _build_transfer_summary(transfer, db)

    links = (
        await db.execute(
            select(TransferContainer).where(TransferContainer.transfer_id == transfer.id)
        )
    ).scalars().all()

    containers: list[ContainerSummary] = []
    for link in links:
        c = await db.get(Container, link.container_id)
        if c:
            containers.append(await _build_summary(c, db))

    return TransferDetail(
        **summary.model_dump(),
        notes=transfer.notes,
        containers=containers,
        created_at=transfer.created_at,
        updated_at=transfer.updated_at,
    )


async def list_transfers(
    house_id: str,
    db: AsyncSession,
    status_filter: str | None = None,
    destination_location_id: str | None = None,
) -> list[TransferSummary]:
    stmt = select(Transfer).where(Transfer.house_id == house_id)
    if status_filter:
        stmt = stmt.where(Transfer.status == status_filter)
    if destination_location_id:
        stmt = stmt.where(Transfer.destination_location_id == destination_location_id)
    stmt = stmt.order_by(Transfer.created_at.desc())

    transfers = (await db.execute(stmt)).scalars().all()
    return [await _build_transfer_summary(t, db) for t in transfers]


async def create_transfer(
    house_id: str,
    user_id: str,
    data: TransferCreate,
    db: AsyncSession,
) -> TransferDetail:
    transfer = Transfer(
        house_id=house_id,
        name=data.name,
        destination_location_id=data.destination_location_id,
        scheduled_date=data.scheduled_date,
        vehicle_volume_liters=Decimal(str(data.vehicle_volume_liters)) if data.vehicle_volume_liters else None,
        notes=data.notes,
        status="planned",
        created_by=user_id,
    )
    db.add(transfer)
    await db.flush()

    for cid in data.container_ids:
        db.add(TransferContainer(transfer_id=transfer.id, container_id=cid, added_manually=True))

    await db.commit()
    await db.refresh(transfer)
    return await _build_transfer_detail(transfer, db)


async def get_transfer_detail(transfer_id: str, house_id: str, db: AsyncSession) -> TransferDetail:
    transfer = await _get_transfer_or_404(transfer_id, house_id, db)
    return await _build_transfer_detail(transfer, db)


async def update_transfer(
    transfer_id: str,
    house_id: str,
    data: TransferUpdate,
    db: AsyncSession,
) -> TransferDetail:
    transfer = await _get_transfer_or_404(transfer_id, house_id, db)
    if transfer.status in ("completed", "cancelled"):
        raise HTTPException(
            status_code=400,
            detail={"detail": "Cannot modify completed or cancelled transfer", "code": "INVALID_STATUS"},
        )

    if data.name is not None:
        transfer.name = data.name
    if data.destination_location_id is not None:
        transfer.destination_location_id = data.destination_location_id
    if data.scheduled_date is not None:
        transfer.scheduled_date = data.scheduled_date
    if data.vehicle_volume_liters is not None:
        transfer.vehicle_volume_liters = Decimal(str(data.vehicle_volume_liters))
    if data.notes is not None:
        transfer.notes = data.notes

    await db.commit()
    await db.refresh(transfer)
    return await _build_transfer_detail(transfer, db)


async def add_containers(
    transfer_id: str,
    house_id: str,
    container_ids: list[str],
    db: AsyncSession,
) -> TransferDetail:
    transfer = await _get_transfer_or_404(transfer_id, house_id, db)
    if transfer.status == "completed":
        raise HTTPException(
            status_code=400,
            detail={"detail": "Transfer already completed", "code": "INVALID_STATUS"},
        )

    existing = set(
        (
            await db.execute(
                select(TransferContainer.container_id).where(
                    TransferContainer.transfer_id == transfer_id
                )
            )
        )
        .scalars()
        .all()
    )

    for cid in container_ids:
        if cid not in existing:
            db.add(TransferContainer(transfer_id=transfer_id, container_id=cid, added_manually=True))

    await db.commit()
    return await _build_transfer_detail(transfer, db)


async def remove_container(
    transfer_id: str,
    container_id: str,
    house_id: str,
    db: AsyncSession,
) -> TransferDetail:
    transfer = await _get_transfer_or_404(transfer_id, house_id, db)

    link = (
        await db.execute(
            select(TransferContainer).where(
                TransferContainer.transfer_id == transfer_id,
                TransferContainer.container_id == container_id,
            )
        )
    ).scalar_one_or_none()

    if not link:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Container not in this transfer", "code": "NOT_FOUND"},
        )

    await db.delete(link)
    await db.commit()
    return await _build_transfer_detail(transfer, db)


async def start_transfer(transfer_id: str, house_id: str, db: AsyncSession) -> TransferDetail:
    transfer = await _get_transfer_or_404(transfer_id, house_id, db)
    if transfer.status != "planned":
        raise HTTPException(
            status_code=400,
            detail={"detail": "Transfer must be in planned status to start", "code": "INVALID_STATUS"},
        )

    transfer.status = "in_progress"

    links = (
        await db.execute(
            select(TransferContainer).where(TransferContainer.transfer_id == transfer_id)
        )
    ).scalars().all()

    for link in links:
        c = await db.get(Container, link.container_id)
        if c and c.status in ("open", "closed", "sealed"):
            c.status = "in_transit"

    await db.commit()
    await db.refresh(transfer)
    return await _build_transfer_detail(transfer, db)


async def _deliver_container_recursive(
    container: Container,
    dest_location_id: str,
    dest_house_id: str,
    db: AsyncSession,
) -> None:
    container.house_id = dest_house_id
    container.current_location_id = dest_location_id
    container.destination_location_id = None
    container.status = "delivered"
    children = (
        await db.execute(select(Container).where(Container.parent_id == container.id))
    ).scalars().all()
    for child in children:
        await _deliver_container_recursive(child, dest_location_id, dest_house_id, db)


async def complete_transfer(transfer_id: str, house_id: str, db: AsyncSession) -> TransferDetail:
    transfer = await _get_transfer_or_404(transfer_id, house_id, db)
    if transfer.status != "in_progress":
        raise HTTPException(
            status_code=400,
            detail={"detail": "Transfer must be in_progress to complete", "code": "INVALID_STATUS"},
        )

    dest_location = None
    dest_house_id = None
    if transfer.destination_location_id:
        dest_location = await db.get(Location, transfer.destination_location_id)
        if dest_location:
            dest_house_id = dest_location.house_id

    transfer.status = "completed"

    links = (
        await db.execute(
            select(TransferContainer).where(TransferContainer.transfer_id == transfer_id)
        )
    ).scalars().all()

    for link in links:
        c = await db.get(Container, link.container_id)
        if c:
            if dest_location and dest_house_id:
                await _deliver_container_recursive(c, dest_location.id, dest_house_id, db)
            else:
                c.status = "delivered"

    await db.commit()
    await db.refresh(transfer)
    return await _build_transfer_detail(transfer, db)


async def plan_transfers(
    house_id: str,
    request: TransferPlanRequest,
    db: AsyncSession,
) -> TransferPlanResponse:
    stmt = (
        select(Container)
        .join(Location, Container.destination_location_id == Location.id)
        .where(
            Container.house_id == house_id,
            Location.house_id == request.destination_house_id,
            Container.status.in_(["closed", "sealed"]),
        )
    )
    containers = list((await db.execute(stmt)).scalars().all())

    bins, unassigned = group_containers_ffd(containers, request.vehicle_volume_liters)

    trips: list[TripPlan] = []
    for i, bin_containers in enumerate(bins):
        total_vol = sum(float(c.volume_liters or 0) for c in bin_containers)
        fill_pct = round(total_vol / request.vehicle_volume_liters * 100, 1)
        scheduled_date = request.scheduled_dates[i] if i < len(request.scheduled_dates) else None
        summaries = [await _build_summary(c, db) for c in bin_containers]
        trips.append(
            TripPlan(
                trip_number=i + 1,
                containers=summaries,
                total_volume_liters=total_vol,
                vehicle_fill_percent=fill_pct,
                scheduled_date=scheduled_date,
            )
        )

    return TransferPlanResponse(
        trips=trips,
        unassigned_containers=[await _build_summary(c, db) for c in unassigned],
        algorithm="FFD",
    )


async def get_location_summary(
    location_id: str,
    house_id: str,
    db: AsyncSession,
) -> LocationSummaryOut:
    loc = await db.get(Location, location_id)
    if not loc:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Location not found", "code": "NOT_FOUND"},
        )

    containers = list(
        (
            await db.execute(
                select(Container).where(
                    Container.house_id == house_id,
                    Container.destination_location_id == location_id,
                )
            )
        )
        .scalars()
        .all()
    )

    total_volume = sum(float(c.volume_liters or 0) for c in containers)
    transferred_count = sum(1 for c in containers if c.status in ("in_transit", "delivered"))

    transfers = (
        await db.execute(
            select(Transfer).where(
                Transfer.house_id == house_id,
                Transfer.destination_location_id == location_id,
                Transfer.status.in_(["planned", "in_progress"]),
            )
        )
    ).scalars().all()

    house = await db.get(House, loc.house_id)
    location_mini = LocationMini(
        id=loc.id,
        name=loc.name,
        house_id=loc.house_id,
        house_name=house.name if house else "",
    )

    return LocationSummaryOut(
        location=location_mini,
        container_count=len(containers),
        total_volume_liters=total_volume,
        transferred_count=transferred_count,
        planned_transfers=[await _build_transfer_summary(t, db) for t in transfers],
        containers=[await _build_summary(c, db) for c in containers],
    )
