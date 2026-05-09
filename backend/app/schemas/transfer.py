# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from datetime import date, datetime
from pydantic import BaseModel

from app.schemas.container import ContainerSummary, LocationMini


class TransferCreate(BaseModel):
    name: str
    destination_location_id: str
    scheduled_date: date | None = None
    vehicle_volume_liters: float | None = None
    notes: str | None = None
    container_ids: list[str] = []


class TransferUpdate(BaseModel):
    name: str | None = None
    destination_location_id: str | None = None
    scheduled_date: date | None = None
    vehicle_volume_liters: float | None = None
    notes: str | None = None


class AddContainersRequest(BaseModel):
    container_ids: list[str]


class TransferPlanRequest(BaseModel):
    destination_house_id: str
    vehicle_volume_liters: float
    scheduled_dates: list[date] = []


class TransferSummary(BaseModel):
    id: str
    name: str
    status: str
    destination_location: LocationMini | None
    scheduled_date: date | None
    vehicle_volume_liters: float | None
    container_count: int
    total_volume_liters: float


class TransferDetail(TransferSummary):
    notes: str | None
    containers: list[ContainerSummary]
    created_at: datetime
    updated_at: datetime


class TripPlan(BaseModel):
    trip_number: int
    containers: list[ContainerSummary]
    total_volume_liters: float
    vehicle_fill_percent: float
    scheduled_date: date | None = None


class TransferPlanResponse(BaseModel):
    trips: list[TripPlan]
    unassigned_containers: list[ContainerSummary]
    algorithm: str = "FFD"


class LocationSummaryOut(BaseModel):
    location: LocationMini
    container_count: int
    total_volume_liters: float
    transferred_count: int
    planned_transfers: list[TransferSummary]
    containers: list[ContainerSummary]
