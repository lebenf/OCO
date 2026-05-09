# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_house_member
from app.models.container import Container
from app.models.house import House
from app.models.item import Item
from app.models.location import Location
from app.models.transfer import Transfer
from app.schemas.dashboard import (
    ContainersByStatus,
    DashboardResponse,
    DestinationHouseStats,
    ItemStats,
    SearchResults,
)
from app.schemas.house import HouseMini
from app.services.container_service import _build_summary as build_container_summary
from app.services.item_service import list_items
from app.services.transfer_service import _build_transfer_summary

router = APIRouter()


@router.get("/houses/{house_id}/dashboard", response_model=DashboardResponse)
async def get_dashboard(
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    house_id = house.id

    status_rows = (
        await db.execute(
            select(Container.status, func.count())
            .where(Container.house_id == house_id)
            .group_by(Container.status)
        )
    ).all()
    by_status: dict[str, int] = {row[0]: row[1] for row in status_rows}
    total_containers = sum(by_status.values())

    items_total = (
        await db.execute(
            select(func.count())
            .select_from(Item)
            .where(Item.house_id == house_id, Item.status == "confirmed")
        )
    ).scalar_one()

    # Group containers by destination_location.house_id
    dest_rows = (
        await db.execute(
            select(Location.house_id, func.count(Container.id), func.sum(Container.volume_liters))
            .join(Container, Container.destination_location_id == Location.id)
            .where(Container.house_id == house_id)
            .group_by(Location.house_id)
        )
    ).all()

    dest_house_stats: list[DestinationHouseStats] = []
    for dest_house_id, container_count, total_vol in dest_rows:
        dest_house = await db.get(House, dest_house_id)
        if not dest_house:
            continue
        delivered = (
            await db.execute(
                select(func.count(Container.id))
                .join(Location, Container.destination_location_id == Location.id)
                .where(
                    Container.house_id == house_id,
                    Location.house_id == dest_house_id,
                    Container.status == "delivered",
                )
            )
        ).scalar_one()
        dest_house_stats.append(
            DestinationHouseStats(
                house=HouseMini(id=dest_house.id, name=dest_house.name, is_disposal=dest_house.is_disposal),
                container_count=container_count,
                total_volume_liters=float(total_vol or 0),
                delivered=delivered,
            )
        )

    upcoming = (
        await db.execute(
            select(Transfer)
            .where(
                Transfer.house_id == house_id,
                Transfer.status.in_(["planned", "in_progress"]),
            )
            .order_by(Transfer.scheduled_date.asc().nulls_last(), Transfer.created_at.asc())
            .limit(5)
        )
    ).scalars().all()
    upcoming_summaries = [await _build_transfer_summary(t, db) for t in upcoming]

    recent = (
        await db.execute(
            select(Container)
            .where(Container.house_id == house_id)
            .order_by(Container.created_at.desc())
            .limit(10)
        )
    ).scalars().all()
    recent_summaries = [await build_container_summary(c, db) for c in recent]

    return DashboardResponse(
        containers=ContainersByStatus(total=total_containers, by_status=by_status),
        items=ItemStats(total=items_total),
        by_destination_house=dest_house_stats,
        upcoming_transfers=upcoming_summaries,
        recent_containers=recent_summaries,
    )


@router.get("/houses/{house_id}/search", response_model=SearchResults)
async def global_search(
    q: str = Query(..., min_length=2),
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
):
    house_id = house.id

    items_page = await list_items(house_id, db, status_filter="confirmed", search=q, size=10)

    container_rows = (
        await db.execute(
            select(Container).where(
                Container.house_id == house_id,
                Container.code.ilike(f"%{q}%") | Container.description.ilike(f"%{q}%"),
            ).limit(10)
        )
    ).scalars().all()
    container_summaries = [await build_container_summary(c, db) for c in container_rows]

    return SearchResults(
        query=q,
        items=items_page.items,
        containers=container_summaries,
    )
