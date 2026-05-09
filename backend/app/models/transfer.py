# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.location import Location
    from app.models.transfer_container import TransferContainer


class Transfer(Base):
    __tablename__ = "transfers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    house_id: Mapped[str] = mapped_column(String(36), ForeignKey("houses.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    destination_location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id"), nullable=True, index=True)
    scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    vehicle_volume_liters: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    # planned | in_progress | completed | cancelled
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="planned")
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    destination_location: Mapped["Location | None"] = relationship("Location", back_populates="transfers")
    container_links: Mapped[list["TransferContainer"]] = relationship("TransferContainer", back_populates="transfer", cascade="all, delete-orphan")
