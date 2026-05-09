# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from datetime import datetime
from pydantic import BaseModel


class TempPhotoOut(BaseModel):
    id: str
    url: str


class JobStatusOut(BaseModel):
    id: str
    status: str
    item_id: str | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class InboxCountOut(BaseModel):
    total: int
    pending_ai: int
    ready_for_review: int
    failed: int
