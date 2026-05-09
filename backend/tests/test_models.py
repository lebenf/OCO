# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import select

from app.core.database import Base
import app.models  # noqa: F401
from app.models.user import User
from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.location import Location
from app.models.container import Container
from app.models.category import Category
from app.models.item import Item
from app.models.transfer import Transfer
from app.models.transfer_container import TransferContainer


TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def db_session():
    engine = create_async_engine(TEST_DB_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
async def base_data(db_session: AsyncSession):
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash="hash",
        is_system_admin=True,
    )
    db_session.add(user)
    await db_session.flush()

    house = House(
        name="Test House",
        code_prefix="A",
        created_by=user.id,
    )
    db_session.add(house)
    await db_session.flush()

    return {"user": user, "house": house}


@pytest.mark.asyncio
async def test_migration_applies_on_sqlite(db_session: AsyncSession):
    result = await db_session.execute(select(User))
    assert result.scalars().all() == []


@pytest.mark.asyncio
async def test_user_create(db_session: AsyncSession):
    user = User(username="alice", email="alice@example.com", password_hash="hash")
    db_session.add(user)
    await db_session.commit()

    result = await db_session.execute(select(User).where(User.username == "alice"))
    fetched = result.scalar_one()
    assert fetched.email == "alice@example.com"
    assert fetched.id is not None


@pytest.mark.asyncio
async def test_house_membership_fk_cascade(db_session: AsyncSession, base_data):
    user = base_data["user"]
    house = base_data["house"]

    membership = HouseMembership(house_id=house.id, user_id=user.id, role="admin")
    db_session.add(membership)
    await db_session.commit()

    result = await db_session.execute(select(HouseMembership).where(HouseMembership.house_id == house.id))
    fetched = result.scalar_one()
    assert fetched.role == "admin"


@pytest.mark.asyncio
async def test_container_with_current_and_destination_locations(db_session: AsyncSession, base_data):
    user = base_data["user"]
    house = base_data["house"]

    dest_house = House(name="Dest House", code_prefix="B", created_by=user.id)
    db_session.add(dest_house)
    await db_session.flush()

    current_loc = Location(house_id=house.id, name="Cantina")
    dest_loc = Location(house_id=dest_house.id, name="Soggiorno")
    db_session.add_all([current_loc, dest_loc])
    await db_session.flush()

    container = Container(
        house_id=house.id,
        code="A-001",
        status="open",
        current_location_id=current_loc.id,
        destination_location_id=dest_loc.id,
        created_by=user.id,
    )
    db_session.add(container)
    await db_session.commit()

    result = await db_session.execute(select(Container).where(Container.code == "A-001"))
    fetched = result.scalar_one()
    assert fetched.current_location_id == current_loc.id
    assert fetched.destination_location_id == dest_loc.id


@pytest.mark.asyncio
async def test_container_nesting(db_session: AsyncSession, base_data):
    user = base_data["user"]
    house = base_data["house"]

    parent = Container(house_id=house.id, code="A-001", status="open", nesting_level=0, created_by=user.id)
    db_session.add(parent)
    await db_session.flush()

    child = Container(house_id=house.id, code="A-002", status="open", nesting_level=1, parent_id=parent.id, created_by=user.id)
    db_session.add(child)
    await db_session.commit()

    result = await db_session.execute(select(Container).where(Container.parent_id == parent.id))
    fetched = result.scalar_one()
    assert fetched.code == "A-002"


@pytest.mark.asyncio
async def test_item_fk(db_session: AsyncSession, base_data):
    user = base_data["user"]
    house = base_data["house"]

    container = Container(house_id=house.id, code="A-001", status="open", created_by=user.id)
    db_session.add(container)
    await db_session.flush()

    item = Item(
        container_id=container.id,
        house_id=house.id,
        item_type="single",
        name="Libro di test",
        status="draft",
        created_by=user.id,
    )
    db_session.add(item)
    await db_session.commit()

    result = await db_session.execute(select(Item).where(Item.container_id == container.id))
    fetched = result.scalar_one()
    assert fetched.name == "Libro di test"
    assert fetched.status == "draft"


@pytest.mark.asyncio
async def test_transfer_with_containers(db_session: AsyncSession, base_data):
    user = base_data["user"]
    house = base_data["house"]

    dest_house = House(name="Dest House", code_prefix="B", created_by=user.id)
    db_session.add(dest_house)
    await db_session.flush()

    dest_loc = Location(house_id=dest_house.id, name="Soggiorno")
    db_session.add(dest_loc)
    await db_session.flush()

    container = Container(house_id=house.id, code="A-001", status="closed", created_by=user.id)
    db_session.add(container)
    await db_session.flush()

    transfer = Transfer(
        house_id=house.id,
        name="Primo viaggio",
        destination_location_id=dest_loc.id,
        status="planned",
        created_by=user.id,
    )
    db_session.add(transfer)
    await db_session.flush()

    link = TransferContainer(transfer_id=transfer.id, container_id=container.id, added_manually=True)
    db_session.add(link)
    await db_session.commit()

    result = await db_session.execute(
        select(TransferContainer).where(TransferContainer.transfer_id == transfer.id)
    )
    fetched = result.scalar_one()
    assert fetched.container_id == container.id


@pytest.mark.asyncio
async def test_item_cascade_delete(db_session: AsyncSession, base_data):
    user = base_data["user"]
    house = base_data["house"]

    container = Container(house_id=house.id, code="A-001", status="open", created_by=user.id)
    db_session.add(container)
    await db_session.flush()

    item = Item(container_id=container.id, house_id=house.id, item_type="single", name="X", status="confirmed", created_by=user.id)
    db_session.add(item)
    await db_session.commit()

    await db_session.delete(container)
    await db_session.commit()

    result = await db_session.execute(select(Item))
    assert result.scalars().all() == []
