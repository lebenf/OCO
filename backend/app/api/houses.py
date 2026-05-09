# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user, get_house_admin
from app.models.house import House
from app.models.location import Location
from app.models.user import User
from app.schemas.house import (
    AllLocationsEntry,
    LocationCreate, LocationOut, LocationUpdate,
)
from app.services.house_service import (
    create_location,
    delete_location,
    get_all_locations,
    list_locations,
    update_location,
)

router = APIRouter(prefix="/houses", tags=["houses"])


@router.get("/all-locations", response_model=list[AllLocationsEntry])
async def get_all_locations_endpoint(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AllLocationsEntry]:
    return await get_all_locations(db, current_user.id)


@router.get("/{house_id}/locations", response_model=list[LocationOut])
async def get_locations(
    house: House = Depends(get_house_admin),
    db: AsyncSession = Depends(get_db),
) -> list[LocationOut]:
    return await list_locations(db, house.id)


@router.post("/{house_id}/locations", response_model=LocationOut, status_code=status.HTTP_201_CREATED)
async def post_location(
    body: LocationCreate,
    house: House = Depends(get_house_admin),
    db: AsyncSession = Depends(get_db),
) -> LocationOut:
    loc = await create_location(db, house.id, body)
    return LocationOut.model_validate(loc)


@router.put("/{house_id}/locations/{location_id}", response_model=LocationOut)
async def put_location(
    location_id: str,
    body: LocationUpdate,
    house: House = Depends(get_house_admin),
    db: AsyncSession = Depends(get_db),
) -> LocationOut:
    loc = await db.get(Location, location_id)
    if not loc or loc.house_id != house.id:
        raise HTTPException(status_code=404, detail={"detail": "Location not found", "code": "NOT_FOUND"})
    loc = await update_location(db, loc, body)
    return LocationOut.model_validate(loc)


@router.delete("/{house_id}/locations/{location_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_location(
    location_id: str,
    house: House = Depends(get_house_admin),
    db: AsyncSession = Depends(get_db),
) -> None:
    loc = await db.get(Location, location_id)
    if not loc or loc.house_id != house.id:
        raise HTTPException(status_code=404, detail={"detail": "Location not found", "code": "NOT_FOUND"})
    await delete_location(db, loc)
