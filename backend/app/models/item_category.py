# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.item import Item
    from app.models.category import Category


class ItemCategory(Base):
    __tablename__ = "item_categories"
    __table_args__ = (PrimaryKeyConstraint("item_id", "category_id"),)

    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("items.id", ondelete="CASCADE"), nullable=False)
    category_id: Mapped[str] = mapped_column(String(36), ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)

    item: Mapped["Item"] = relationship("Item", back_populates="category_links")
    category: Mapped["Category"] = relationship("Category", back_populates="item_links")
