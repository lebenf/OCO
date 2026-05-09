# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import math

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.location import Location
from app.models.user import User
from app.schemas.house import (
    AllLocationsEntry,
    HouseCreate, HouseOut, HouseUpdate, HouseMini,
    LocationCreate, LocationOut, LocationUpdate,
    MemberOut,
)
from app.schemas.pagination import Page


async def list_houses(db: AsyncSession, page: int, size: int) -> Page[HouseOut]:
    total = (await db.execute(select(func.count()).select_from(House))).scalar_one()
    rows = (await db.execute(select(House).offset((page - 1) * size).limit(size))).scalars().all()
    return Page(
        items=[HouseOut.model_validate(h) for h in rows],
        total=total,
        page=page,
        pages=max(1, math.ceil(total / size)),
    )


async def create_house(db: AsyncSession, data: HouseCreate, created_by: str) -> House:
    house = House(
        name=data.name,
        description=data.description,
        code_prefix=data.code_prefix,
        created_by=created_by,
    )
    db.add(house)
    await db.commit()
    await db.refresh(house)
    return house


async def update_house(db: AsyncSession, house: House, data: HouseUpdate) -> House:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(house, field, value)
    await db.commit()
    await db.refresh(house)
    return house


async def get_house_members(db: AsyncSession, house_id: str) -> list[MemberOut]:
    rows = (
        await db.execute(
            select(HouseMembership)
            .options(selectinload(HouseMembership.user))
            .where(HouseMembership.house_id == house_id)
        )
    ).scalars().all()
    return [
        MemberOut(user_id=m.user_id, username=m.user.username, email=m.user.email, role=m.role)
        for m in rows
    ]


async def add_member(db: AsyncSession, house_id: str, user_id: str, role: str) -> MemberOut:
    existing = (
        await db.execute(
            select(HouseMembership).where(
                HouseMembership.house_id == house_id,
                HouseMembership.user_id == user_id,
            )
        )
    ).scalar_one_or_none()

    if existing:
        existing.role = role
        await db.commit()
        membership = existing
    else:
        membership = HouseMembership(house_id=house_id, user_id=user_id, role=role)
        db.add(membership)
        await db.commit()

    user = await db.get(User, user_id)
    return MemberOut(user_id=user_id, username=user.username, email=user.email, role=role)


async def remove_member(db: AsyncSession, house_id: str, user_id: str) -> None:
    membership = (
        await db.execute(
            select(HouseMembership).where(
                HouseMembership.house_id == house_id,
                HouseMembership.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if membership:
        await db.delete(membership)
        await db.commit()


# --- Locations ---

async def list_locations(db: AsyncSession, house_id: str) -> list[LocationOut]:
    rows = (
        await db.execute(select(Location).where(Location.house_id == house_id))
    ).scalars().all()
    return [LocationOut.model_validate(loc) for loc in rows]


async def create_location(db: AsyncSession, house_id: str, data: LocationCreate) -> Location:
    loc = Location(house_id=house_id, name=data.name, description=data.description)
    db.add(loc)
    await db.commit()
    await db.refresh(loc)
    return loc


async def update_location(db: AsyncSession, loc: Location, data: LocationUpdate) -> Location:
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(loc, field, value)
    await db.commit()
    await db.refresh(loc)
    return loc


async def delete_location(db: AsyncSession, loc: Location) -> None:
    await db.delete(loc)
    await db.commit()


async def get_all_locations(db: AsyncSession, user_id: str) -> list[AllLocationsEntry]:
    """Return all locations grouped by house, for houses the user is a member of."""
    memberships = (
        await db.execute(
            select(HouseMembership.house_id).where(HouseMembership.user_id == user_id)
        )
    ).scalars().all()

    house_ids = list(memberships)
    houses = (
        await db.execute(select(House).where(House.id.in_(house_ids)))
    ).scalars().all()

    result: list[AllLocationsEntry] = []
    for house in sorted(houses, key=lambda h: (h.is_disposal, h.name)):
        locs = (
            await db.execute(
                select(Location).where(Location.house_id == house.id, Location.is_active == True)
            )
        ).scalars().all()
        result.append(
            AllLocationsEntry(
                house=HouseMini(id=house.id, name=house.name, is_disposal=house.is_disposal),
                locations=[LocationOut.model_validate(loc) for loc in locs],
            )
        )
    return result
