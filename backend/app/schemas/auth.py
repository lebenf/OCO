# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    username: str
    password: str


class HouseMini(BaseModel):
    id: str
    name: str
    role: str


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    is_system_admin: bool
    preferred_language: str
    houses: list[HouseMini]

    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    preferred_language: str
