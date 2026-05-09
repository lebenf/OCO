# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.house import House
from app.models.house_membership import HouseMembership


@pytest.fixture
async def house_with_member(db_session: AsyncSession, admin_user):
    house = House(name="CatHouse", code_prefix="C", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))
    await db_session.commit()
    return house


@pytest.mark.asyncio
async def test_list_categories_empty(auth_client: AsyncClient, house_with_member):
    resp = await auth_client.get(f"/api/houses/{house_with_member.id}/categories")
    assert resp.status_code == 200
    assert resp.json() == []


@pytest.mark.asyncio
async def test_create_category(auth_client: AsyncClient, house_with_member):
    resp = await auth_client.post(
        f"/api/houses/{house_with_member.id}/categories",
        json={"name": "Elettronica", "icon": "💻"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Elettronica"
    assert data["icon"] == "💻"
    assert data["is_system"] is False


@pytest.mark.asyncio
async def test_list_categories_after_create(auth_client: AsyncClient, house_with_member):
    await auth_client.post(
        f"/api/houses/{house_with_member.id}/categories",
        json={"name": "Libri"},
    )
    resp = await auth_client.get(f"/api/houses/{house_with_member.id}/categories")
    assert resp.status_code == 200
    names = [c["name"] for c in resp.json()]
    assert "Libri" in names


@pytest.mark.asyncio
async def test_update_category(auth_client: AsyncClient, house_with_member):
    create = await auth_client.post(
        f"/api/houses/{house_with_member.id}/categories",
        json={"name": "Cucina"},
    )
    cat_id = create.json()["id"]
    resp = await auth_client.put(
        f"/api/houses/{house_with_member.id}/categories/{cat_id}",
        json={"name": "Cucina & Bagno", "icon": "🍳"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Cucina & Bagno"
    assert resp.json()["icon"] == "🍳"


@pytest.mark.asyncio
async def test_update_category_not_found(auth_client: AsyncClient, house_with_member):
    resp = await auth_client.put(
        f"/api/houses/{house_with_member.id}/categories/nonexistent",
        json={"name": "X"},
    )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_category(auth_client: AsyncClient, house_with_member):
    create = await auth_client.post(
        f"/api/houses/{house_with_member.id}/categories",
        json={"name": "ToDelete"},
    )
    cat_id = create.json()["id"]
    resp = await auth_client.delete(f"/api/houses/{house_with_member.id}/categories/{cat_id}")
    assert resp.status_code == 204

    # Verify it's gone
    list_resp = await auth_client.get(f"/api/houses/{house_with_member.id}/categories")
    names = [c["name"] for c in list_resp.json()]
    assert "ToDelete" not in names


@pytest.mark.asyncio
async def test_delete_category_not_found(auth_client: AsyncClient, house_with_member):
    resp = await auth_client.delete(f"/api/houses/{house_with_member.id}/categories/nonexistent")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_system_category_forbidden(auth_client: AsyncClient, house_with_member, db_session):
    sys_cat = Category(
        house_id=house_with_member.id, name="SysCategory", is_system=True
    )
    db_session.add(sys_cat)
    await db_session.commit()

    resp = await auth_client.delete(f"/api/houses/{house_with_member.id}/categories/{sys_cat.id}")
    assert resp.status_code == 400
    assert resp.json()["detail"]["code"] == "SYSTEM_CATEGORY"
