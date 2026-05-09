# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pydantic import BaseModel

from app.schemas.container import ContainerSummary, LocationMini
from app.schemas.house import HouseMini
from app.schemas.item import ItemSummary
from app.schemas.transfer import TransferSummary


class ContainersByStatus(BaseModel):
    total: int
    by_status: dict[str, int]


class ItemStats(BaseModel):
    total: int


class DestinationHouseStats(BaseModel):
    house: HouseMini
    container_count: int
    total_volume_liters: float
    delivered: int


class DashboardResponse(BaseModel):
    containers: ContainersByStatus
    items: ItemStats
    by_destination_house: list[DestinationHouseStats]
    upcoming_transfers: list[TransferSummary]
    recent_containers: list[ContainerSummary]


class SearchResults(BaseModel):
    query: str
    items: list[ItemSummary]
    containers: list[ContainerSummary]
