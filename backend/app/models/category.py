# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.item_category import ItemCategory


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    house_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("houses.id", ondelete="CASCADE"), nullable=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    name_translations: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parent_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    is_system: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent", foreign_keys="Category.parent_id")
    parent: Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side="Category.id", foreign_keys="Category.parent_id")
    item_links: Mapped[list["ItemCategory"]] = relationship("ItemCategory", back_populates="category")
