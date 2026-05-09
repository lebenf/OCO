# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pydantic import BaseModel


class HouseCreate(BaseModel):
    name: str
    description: str | None = None
    code_prefix: str  # single char


class HouseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    code_prefix: str | None = None


class HouseOut(BaseModel):
    id: str
    name: str
    description: str | None
    code_prefix: str
    container_sequence: int
    is_disposal: bool
    created_by: str

    model_config = {"from_attributes": True}


class MembershipCreate(BaseModel):
    user_id: str
    role: str  # admin | member


class MemberOut(BaseModel):
    user_id: str
    username: str
    email: str
    role: str


class LocationCreate(BaseModel):
    name: str
    description: str | None = None


class LocationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class LocationOut(BaseModel):
    id: str
    house_id: str
    name: str
    description: str | None
    is_active: bool

    model_config = {"from_attributes": True}


class HouseMini(BaseModel):
    id: str
    name: str
    is_disposal: bool

    model_config = {"from_attributes": True}


class AllLocationsEntry(BaseModel):
    house: HouseMini
    locations: list[LocationOut]
