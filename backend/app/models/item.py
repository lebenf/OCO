# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.container import Container
    from app.models.item_photo import ItemPhoto
    from app.models.item_category import ItemCategory
    from app.models.ai_analysis_job import AIAnalysisJob


class Item(Base):
    __tablename__ = "items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    container_id: Mapped[str] = mapped_column(String(36), ForeignKey("containers.id", ondelete="CASCADE"), nullable=False, index=True)
    house_id: Mapped[str] = mapped_column(String(36), ForeignKey("houses.id", ondelete="CASCADE"), nullable=False, index=True)
    # draft | draft_ai_done | draft_ai_failed | confirmed
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="draft", index=True)
    item_type: Mapped[str] = mapped_column(String(20), nullable=False)  # single | composite | set | collection
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    brand: Mapped[str | None] = mapped_column(String(100), nullable=True)
    model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    color: Mapped[str | None] = mapped_column(String(100), nullable=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    ai_confidence: Mapped[Decimal | None] = mapped_column(Numeric(3, 2), nullable=True)
    ai_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ai_job_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("ai_analysis_jobs.id", ondelete="SET NULL"), nullable=True)
    ai_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    ai_result_raw: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON
    tags: Mapped[str | None] = mapped_column(Text, nullable=True)  # JSON array
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_by: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())

    container: Mapped["Container"] = relationship("Container", back_populates="items")
    photos: Mapped[list["ItemPhoto"]] = relationship("ItemPhoto", back_populates="item", cascade="all, delete-orphan")
    category_links: Mapped[list["ItemCategory"]] = relationship("ItemCategory", back_populates="item", cascade="all, delete-orphan")
    ai_job: Mapped["AIAnalysisJob | None"] = relationship("AIAnalysisJob", back_populates="items", foreign_keys="Item.ai_job_id")
