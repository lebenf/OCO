# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import io
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.deps import get_current_user, get_house_member
from app.models.ai_analysis_job import AIAnalysisJob
from app.models.house import House
from app.models.item import Item
from app.models.user import User
from app.schemas.ai import InboxCountOut, JobStatusOut, TempPhotoOut

router = APIRouter(prefix="/houses", tags=["ai"])


@router.post(
    "/{house_id}/ai/temp-photos",
    response_model=list[TempPhotoOut],
    status_code=status.HTTP_201_CREATED,
)
async def upload_temp_photos(
    files: list[UploadFile] = File(...),
    house: House = Depends(get_house_member),
    current_user: User = Depends(get_current_user),
) -> list[TempPhotoOut]:
    results: list[TempPhotoOut] = []
    temp_dir = Path(settings.STORAGE_PATH) / "temp"
    temp_dir.mkdir(parents=True, exist_ok=True)

    for file in files:
        content = await file.read()
        try:
            img = Image.open(io.BytesIO(content)).convert("RGB")
        except Exception:
            raise HTTPException(
                status_code=400,
                detail={"detail": "Invalid image file", "code": "INVALID_IMAGE"},
            )

        max_px = 1920
        if img.width > max_px or img.height > max_px:
            img.thumbnail((max_px, max_px), Image.LANCZOS)

        photo_id = str(uuid.uuid4())
        filename = f"{photo_id}.jpg"
        abs_path = temp_dir / filename
        img.save(str(abs_path), "JPEG", quality=85)

        results.append(TempPhotoOut(
            id=photo_id,
            url=f"/media/temp/{filename}",
        ))

    return results


@router.get("/{house_id}/inbox/count", response_model=InboxCountOut)
async def get_inbox_count(
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> InboxCountOut:
    rows = (
        await db.execute(
            select(Item.status, func.count().label("n"))
            .where(
                Item.house_id == house.id,
                Item.status.in_(["draft", "draft_ai_done", "draft_ai_failed"]),
            )
            .group_by(Item.status)
        )
    ).all()
    counts: dict[str, int] = {r.status: r.n for r in rows}
    return InboxCountOut(
        total=sum(counts.values()),
        pending_ai=counts.get("draft", 0),
        ready_for_review=counts.get("draft_ai_done", 0),
        failed=counts.get("draft_ai_failed", 0),
    )


@router.get("/{house_id}/ai/jobs/{job_id}", response_model=JobStatusOut)
async def get_job_status(
    job_id: str,
    house: House = Depends(get_house_member),
    db: AsyncSession = Depends(get_db),
) -> JobStatusOut:
    job = await db.get(AIAnalysisJob, job_id)
    if not job or job.house_id != house.id:
        raise HTTPException(
            status_code=404,
            detail={"detail": "Job not found", "code": "NOT_FOUND"},
        )
    return JobStatusOut(
        id=job.id,
        status=job.status,
        item_id=job.item_id,
        error_message=job.error_message,
        created_at=job.created_at,
        completed_at=job.completed_at,
    )
