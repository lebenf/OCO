# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str
    icon: str | None = None
    parent_id: str | None = None


class CategoryUpdate(BaseModel):
    name: str | None = None
    icon: str | None = None
    parent_id: str | None = None


class CategoryOut(BaseModel):
    id: str
    name: str
    icon: str | None = None
    parent_id: str | None = None
    is_system: bool
    house_id: str | None = None
