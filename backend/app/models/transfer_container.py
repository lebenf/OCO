# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.transfer import Transfer
    from app.models.container import Container


class TransferContainer(Base):
    __tablename__ = "transfer_containers"
    __table_args__ = (PrimaryKeyConstraint("transfer_id", "container_id"),)

    transfer_id: Mapped[str] = mapped_column(String(36), ForeignKey("transfers.id", ondelete="CASCADE"), nullable=False)
    container_id: Mapped[str] = mapped_column(String(36), ForeignKey("containers.id", ondelete="CASCADE"), nullable=False)
    added_manually: Mapped[bool] = mapped_column(Boolean, default=True)

    transfer: Mapped["Transfer"] = relationship("Transfer", back_populates="container_links")
    container: Mapped["Container"] = relationship("Container", back_populates="transfer_links")
