# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator

from app.core.sanitize import sanitize_name


class ContainerCreate(BaseModel):
    parent_id: str | None = None
    current_location_id: str | None = None
    destination_location_id: str | None = None
    width_cm: Decimal | None = None
    depth_cm: Decimal | None = None
    height_cm: Decimal | None = None
    description: str | None = None

    @field_validator("description", mode="before")
    @classmethod
    def _sanitize(cls, v: str | None) -> str | None:
        return sanitize_name(v) if v is not None else v


class ContainerUpdate(BaseModel):
    parent_id: str | None = None
    current_location_id: str | None = None
    destination_location_id: str | None = None
    width_cm: Decimal | None = None
    depth_cm: Decimal | None = None
    height_cm: Decimal | None = None
    description: str | None = None

    @field_validator("description", mode="before")
    @classmethod
    def _sanitize(cls, v: str | None) -> str | None:
        return sanitize_name(v) if v is not None else v


class ContainerClose(BaseModel):
    current_location_id: str | None = None
    destination_location_id: str | None = None


class LocationMini(BaseModel):
    id: str
    name: str
    house_id: str
    house_name: str


class ContainerMini(BaseModel):
    id: str
    code: str
    status: str


class PhotoOut(BaseModel):
    id: str
    url: str
    phase: str | None = None
    sort_order: int


class ItemSummaryOut(BaseModel):
    id: str
    name: str
    status: str
    item_type: str


class UserMini(BaseModel):
    id: str
    username: str


class ContainerSummary(BaseModel):
    id: str
    code: str
    status: str
    current_location: LocationMini | None = None
    destination_location: LocationMini | None = None
    item_count: int
    volume_liters: float | None = None
    cover_photo_url: str | None = None
    nesting_level: int
    children_count: int


class ContainerDetail(ContainerSummary):
    description: str | None = None
    width_cm: float | None = None
    depth_cm: float | None = None
    height_cm: float | None = None
    photos: list[PhotoOut]
    items: list[ItemSummaryOut]
    children: list[ContainerSummary]
    parent: ContainerMini | None = None
    volume_calculated: float
    created_by: UserMini
    created_at: datetime
    updated_at: datetime
