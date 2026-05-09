# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.limiter import limiter
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import LoginRequest, UpdateProfileRequest, UserProfile
from app.services.auth_service import build_user_profile, get_user_by_username

router = APIRouter(prefix="/auth", tags=["auth"])

_COOKIE_KWARGS = dict(httponly=True, samesite="lax", secure=False)


def _set_auth_cookies(response: Response, user_id: str) -> None:
    response.set_cookie(
        "access_token",
        create_access_token(user_id),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_COOKIE_KWARGS,
    )
    response.set_cookie(
        "refresh_token",
        create_refresh_token(user_id),
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        path="/api/auth",
        **_COOKIE_KWARGS,
    )


def _clear_auth_cookies(response: Response) -> None:
    response.delete_cookie("access_token", **_COOKIE_KWARGS)
    response.delete_cookie("refresh_token", path="/api/auth", **_COOKIE_KWARGS)


@router.post("/login")
@limiter.limit(settings.LOGIN_RATE_LIMIT)
async def login(
    request: Request,
    body: LoginRequest,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    user = await get_user_by_username(db, body.username)
    if not user or not user.is_active or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Invalid credentials", "code": "INVALID_CREDENTIALS"},
        )
    _set_auth_cookies(response, user.id)
    profile = await build_user_profile(db, user.id)
    return {"user": profile.model_dump()}


@router.post("/logout")
async def logout(
    response: Response,
    current_user: User = Depends(get_current_user),
) -> dict:
    _clear_auth_cookies(response)
    return {"ok": True}


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> dict:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Missing refresh token", "code": "MISSING_REFRESH_TOKEN"},
        )
    try:
        payload = decode_token(token)
        if payload.get("type") != "refresh":
            raise ValueError("wrong token type")
        user_id: str = payload["sub"]
    except (JWTError, KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "Invalid refresh token", "code": "INVALID_REFRESH_TOKEN"},
        )

    user = await db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"detail": "User not found or inactive", "code": "USER_INACTIVE"},
        )

    response.set_cookie(
        "access_token",
        create_access_token(user_id),
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **_COOKIE_KWARGS,
    )
    return {"ok": True}


@router.get("/me", response_model=UserProfile)
async def me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    return await build_user_profile(db, current_user.id)


@router.put("/me", response_model=UserProfile)
async def update_me(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfile:
    current_user.preferred_language = body.preferred_language
    await db.commit()
    return await build_user_profile(db, current_user.id)
