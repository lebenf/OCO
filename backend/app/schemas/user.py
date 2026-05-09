# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    is_system_admin: bool = False


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None
    is_system_admin: bool | None = None
    preferred_language: str | None = None


class ResetPasswordRequest(BaseModel):
    new_password: str


class UserOut(BaseModel):
    id: str
    username: str
    email: str
    is_system_admin: bool
    preferred_language: str
    is_active: bool

    model_config = {"from_attributes": True}
