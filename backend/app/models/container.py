# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, SmallInteger, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.house import House
    from app.models.location import Location
    from app.models.container_photo import ContainerPhoto
    from app.models.item import Item
    from app.models.transfer_container import TransferContainer


class Container(Base):
    __tablename__ = "containers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    house_id: Mapped[str] = mapped_column(String(36), ForeignKey("houses.id", ondelete="CASCADE"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("containers.id", ondelete="SET NULL"), nullable=True, index=True)
    nesting_level: Mapped[int] = mapped_column(SmallInteger, default=0)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", index=True)
    current_location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    destination_location_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("locations.id", ondelete="SET NULL"), nullable=True, index=True)
    width_cm: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    depth_cm: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    height_cm: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    volume_liters: Mapped[Decimal | None] = mapped_column(Numeric(10, 3), nullable=True)
    volume_estimated_by_ai: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    cover_photo_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    house: Mapped["House"] = relationship("House", back_populates="containers")
    current_location: Mapped["Location | None"] = relationship("Location", foreign_keys="Container.current_location_id", back_populates="containers_current")
    destination_location: Mapped["Location | None"] = relationship("Location", foreign_keys="Container.destination_location_id", back_populates="containers_destination")
    photos: Mapped[list["ContainerPhoto"]] = relationship("ContainerPhoto", back_populates="container", cascade="all, delete-orphan")
    items: Mapped[list["Item"]] = relationship("Item", back_populates="container", cascade="all, delete-orphan")
    children: Mapped[list["Container"]] = relationship("Container", back_populates="parent", foreign_keys="Container.parent_id")
    parent: Mapped["Container | None"] = relationship("Container", back_populates="children", remote_side="Container.id", foreign_keys="Container.parent_id")
    transfer_links: Mapped[list["TransferContainer"]] = relationship("TransferContainer", back_populates="container")
