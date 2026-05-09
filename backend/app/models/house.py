# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.house_membership import HouseMembership
    from app.models.location import Location
    from app.models.container import Container


class House(Base):
    __tablename__ = "houses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    code_prefix: Mapped[str] = mapped_column(String(1), nullable=False)
    container_sequence: Mapped[int] = mapped_column(Integer, default=0)
    is_disposal: Mapped[bool] = mapped_column(Boolean, default=False)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    memberships: Mapped[list["HouseMembership"]] = relationship("HouseMembership", back_populates="house")
    locations: Mapped[list["Location"]] = relationship("Location", back_populates="house")
    containers: Mapped[list["Container"]] = relationship("Container", back_populates="house")
