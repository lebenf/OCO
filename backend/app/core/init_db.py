# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import asyncio
import logging
import uuid

from sqlalchemy import select

from app.core.config import settings
from app.core.database import AsyncSessionLocal, engine
from app.core.database import Base
from app.core.security import hash_password
import app.models  # noqa: F401

logger = logging.getLogger(__name__)

DISPOSAL_LOCATIONS = [
    "Smaltimento",
    "Donazione",
    "Vendita",
]


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        from app.models.house import House
        from app.models.house_membership import HouseMembership
        from app.models.location import Location
        from app.models.user import User

        result = await session.execute(
            select(User).where(User.username == settings.INITIAL_ADMIN_USERNAME)
        )
        existing = result.scalar_one_or_none()

        if existing is None:
            admin = User(
                id=str(uuid.uuid4()),
                username=settings.INITIAL_ADMIN_USERNAME,
                email=settings.INITIAL_ADMIN_EMAIL,
                password_hash=hash_password(settings.INITIAL_ADMIN_PASSWORD),
                is_system_admin=True,
                preferred_language="it",
                is_active=True,
            )
            session.add(admin)
            await session.flush()
            logger.info("Admin user created: %s", settings.INITIAL_ADMIN_USERNAME)
        else:
            admin = existing
            logger.info("Admin user already exists: %s", settings.INITIAL_ADMIN_USERNAME)

        disposal_house = (
            await session.execute(select(House).where(House.is_disposal == True))
        ).scalar_one_or_none()

        if disposal_house is None:
            disposal_house = House(
                id=str(uuid.uuid4()),
                name="Smaltimento",
                description="Casa virtuale per smaltimento, donazione e vendita",
                code_prefix="X",
                is_disposal=True,
                created_by=admin.id,
            )
            session.add(disposal_house)
            await session.flush()

            membership = HouseMembership(
                house_id=disposal_house.id,
                user_id=admin.id,
                role="admin",
            )
            session.add(membership)

            for loc_name in DISPOSAL_LOCATIONS:
                session.add(Location(
                    id=str(uuid.uuid4()),
                    house_id=disposal_house.id,
                    name=loc_name,
                ))

            logger.info("Disposal house created with default locations")
        else:
            logger.info("Disposal house already exists")

        await session.commit()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_db())
