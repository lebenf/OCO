# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.house import House


class HouseMembership(Base):
    __tablename__ = "house_memberships"
    __table_args__ = (UniqueConstraint("house_id", "user_id"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    house_id: Mapped[str] = mapped_column(String(36), ForeignKey("houses.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # admin | member
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    house: Mapped["House"] = relationship("House", back_populates="memberships")
    user: Mapped["User"] = relationship("User", back_populates="memberships")
