# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.house import House
    from app.models.container import Container
    from app.models.transfer import Transfer


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    house_id: Mapped[str] = mapped_column(String(36), ForeignKey("houses.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    house: Mapped["House"] = relationship("House", back_populates="locations")
    containers_current: Mapped[list["Container"]] = relationship("Container", foreign_keys="Container.current_location_id", back_populates="current_location")
    containers_destination: Mapped[list["Container"]] = relationship("Container", foreign_keys="Container.destination_location_id", back_populates="destination_location")
    transfers: Mapped[list["Transfer"]] = relationship("Transfer", back_populates="destination_location")
