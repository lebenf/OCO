# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, field_validator

from app.core.sanitize import sanitize_name, sanitize_text


class CategoryMini(BaseModel):
    id: str
    name: str
    icon: str | None = None


class ItemPhotoOut(BaseModel):
    id: str
    url: str
    is_primary: bool
    sort_order: int


class ItemCreate(BaseModel):
    item_type: str = "single"
    hint_type: str = "auto"
    photo_ids: list[str] = []
    language: str = "it"
    name: str = "placeholder"


class ItemBatchCreate(BaseModel):
    items: list[ItemCreate]


class ItemUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    brand: str | None = None
    model: str | None = None
    author: str | None = None
    title: str | None = None
    color: str | None = None
    quantity: int | None = None
    item_type: str | None = None
    notes: str | None = None
    tags: list[str] | None = None
    category_ids: list[str] | None = None

    @field_validator("name", "brand", "model", "author", "title", "color", mode="before")
    @classmethod
    def _san_name(cls, v: str | None) -> str | None:
        return sanitize_name(v) if v is not None else v

    @field_validator("description", "notes", mode="before")
    @classmethod
    def _san_text(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v is not None else v


class ItemConfirm(BaseModel):
    name: str
    description: str | None = None
    brand: str | None = None
    model: str | None = None
    author: str | None = None
    title: str | None = None
    color: str | None = None
    quantity: int = 1
    item_type: str = "single"
    notes: str | None = None
    tags: list[str] | None = None
    category_ids: list[str] | None = None

    @field_validator("name", "brand", "model", "author", "title", "color", mode="before")
    @classmethod
    def _san_name(cls, v: str | None) -> str | None:
        return sanitize_name(v) if v is not None else v

    @field_validator("description", "notes", mode="before")
    @classmethod
    def _san_text(cls, v: str | None) -> str | None:
        return sanitize_text(v) if v is not None else v


class ItemSummary(BaseModel):
    id: str
    name: str
    status: str
    item_type: str
    brand: str | None = None
    color: str | None = None
    quantity: int
    ai_generated: bool
    container_id: str
    primary_photo_url: str | None = None
    categories: list[CategoryMini] = []


class ItemDetail(ItemSummary):
    description: str | None = None
    model: str | None = None
    author: str | None = None
    title: str | None = None
    ai_confidence: float | None = None
    ai_provider: str | None = None
    ai_error: str | None = None
    ai_result_raw: str | None = None
    notes: str | None = None
    tags: list[str] = []
    photos: list[ItemPhotoOut] = []
    created_at: datetime
    updated_at: datetime


class DraftItemSummary(BaseModel):
    id: str
    item_type: str
    status: str
    ai_error: str | None = None
    primary_photo_url: str | None = None
    ai_result: dict | None = None
    created_at: datetime


class ContainerInboxGroup(BaseModel):
    container_id: str
    container_code: str
    items: list[DraftItemSummary]


class InboxResponse(BaseModel):
    total: int
    pending_ai: int
    ready_for_review: int
    failed: int
    by_container: list[ContainerInboxGroup]


class RetryAIOut(BaseModel):
    job_id: str


class ConfirmAllOut(BaseModel):
    confirmed: int
    skipped_failed: int
    skipped_pending: int
