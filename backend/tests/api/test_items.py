# SPDX-License-Identifier: AGPL-3.0-or-later
# Copyright 2026 Lorenzo Benfenati
import json
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.house import House
from app.models.house_membership import HouseMembership
from app.models.container import Container
from app.models.item import Item
from app.models.ai_analysis_job import AIAnalysisJob


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
async def house_with_container(db_session: AsyncSession, admin_user):
    house = House(name="Test House", code_prefix="T", created_by=admin_user.id)
    db_session.add(house)
    await db_session.flush()
    db_session.add(HouseMembership(house_id=house.id, user_id=admin_user.id, role="admin"))
    await db_session.flush()
    container = Container(house_id=house.id, code="T-001", status="open", nesting_level=0, created_by=admin_user.id)
    db_session.add(container)
    await db_session.commit()
    return house, container


@pytest.fixture
async def item_client(auth_client: AsyncClient, house_with_container):
    house, container = house_with_container
    return auth_client, house, container


# ── Create draft ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_draft_item(item_client):
    client, house, container = item_client
    resp = await client.post(
        f"/api/houses/{house.id}/containers/{container.id}/items",
        json={"item_type": "single", "hint_type": "auto", "photo_ids": [], "language": "it"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["status"] == "draft"
    assert data["item_type"] == "single"


@pytest.mark.asyncio
async def test_create_batch_items(item_client):
    client, house, container = item_client
    resp = await client.post(
        f"/api/houses/{house.id}/containers/{container.id}/items/batch",
        json={"items": [
            {"item_type": "single", "hint_type": "auto", "photo_ids": []},
            {"item_type": "book", "hint_type": "book", "photo_ids": []},
        ]},
    )
    assert resp.status_code == 201
    assert len(resp.json()) == 2


# ── Confirm ───────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_confirm_item(item_client):
    client, house, container = item_client
    created = (await client.post(
        f"/api/houses/{house.id}/containers/{container.id}/items",
        json={"item_type": "single", "hint_type": "auto", "photo_ids": []},
    )).json()

    resp = await client.put(
        f"/api/houses/{house.id}/items/{created['id']}/confirm",
        json={"name": "Monitor LG", "description": "Nice monitor", "quantity": 1, "item_type": "single"},
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "confirmed"
    assert resp.json()["name"] == "Monitor LG"


# ── Update ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_item(item_client):
    client, house, container = item_client
    created = (await client.post(
        f"/api/houses/{house.id}/containers/{container.id}/items",
        json={"item_type": "single", "hint_type": "auto", "photo_ids": []},
    )).json()

    resp = await client.put(
        f"/api/houses/{house.id}/items/{created['id']}",
        json={"name": "Updated name", "brand": "Sony"},
    )
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated name"
    assert resp.json()["brand"] == "Sony"


# ── Delete ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_delete_item(item_client):
    client, house, container = item_client
    created = (await client.post(
        f"/api/houses/{house.id}/containers/{container.id}/items",
        json={"item_type": "single", "hint_type": "auto", "photo_ids": []},
    )).json()

    resp = await client.delete(f"/api/houses/{house.id}/items/{created['id']}")
    assert resp.status_code == 204

    get_resp = await client.get(f"/api/houses/{house.id}/items/{created['id']}")
    assert get_resp.status_code == 404


# ── Retry AI ──────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_retry_ai(db_session: AsyncSession, item_client):
    client, house, container = item_client
    created = (await client.post(
        f"/api/houses/{house.id}/containers/{container.id}/items",
        json={"item_type": "single", "hint_type": "auto", "photo_ids": []},
    )).json()

    # Manually set item to draft_ai_failed
    item = await db_session.get(Item, created["id"])
    item.status = "draft_ai_failed"
    item.ai_error = "timeout"
    await db_session.commit()

    resp = await client.post(f"/api/houses/{house.id}/items/{created['id']}/retry-ai")
    assert resp.status_code == 200
    assert resp.json()["job_id"]

    await db_session.refresh(item)
    assert item.status == "draft"
    assert item.ai_error is None


@pytest.mark.asyncio
async def test_retry_ai_on_non_failed_rejected(item_client):
    client, house, container = item_client
    created = (await client.post(
        f"/api/houses/{house.id}/containers/{container.id}/items",
        json={"item_type": "single", "hint_type": "auto", "photo_ids": []},
    )).json()

    resp = await client.post(f"/api/houses/{house.id}/items/{created['id']}/retry-ai")
    assert resp.status_code == 400


# ── Confirm-all ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_confirm_all(db_session: AsyncSession, item_client):
    client, house, container = item_client

    # Create 3 items in different states
    ai_result = json.dumps({"name": "Item AI", "description": "", "confidence": 0.9})
    for i in range(3):
        item = Item(
            house_id=house.id,
            container_id=container.id,
            status="draft_ai_done",
            item_type="single",
            name=f"item_{i}",
            created_by=(await db_session.get(House, house.id)).created_by,
            ai_result_raw=ai_result,
        )
        db_session.add(item)
    failed_item = Item(
        house_id=house.id,
        container_id=container.id,
        status="draft_ai_failed",
        item_type="single",
        name="failed",
        created_by=(await db_session.get(House, house.id)).created_by,
    )
    db_session.add(failed_item)
    await db_session.commit()

    resp = await client.post(f"/api/houses/{house.id}/containers/{container.id}/confirm-all")
    assert resp.status_code == 200
    data = resp.json()
    assert data["confirmed"] == 3
    assert data["skipped_failed"] == 1
    assert data["skipped_pending"] == 0


# ── Search / list ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_search_excludes_drafts_by_default(db_session: AsyncSession, item_client):
    client, house, container = item_client

    for s in ("confirmed", "draft", "draft_ai_done"):
        db_session.add(Item(
            house_id=house.id,
            container_id=container.id,
            status=s,
            item_type="single",
            name=f"item_{s}",
            created_by=(await db_session.get(House, house.id)).created_by,
        ))
    await db_session.commit()

    resp = await client.get(f"/api/houses/{house.id}/items")
    assert resp.status_code == 200
    statuses = [i["status"] for i in resp.json()["items"]]
    assert all(s == "confirmed" for s in statuses)


@pytest.mark.asyncio
async def test_search_by_name(db_session: AsyncSession, item_client):
    client, house, container = item_client

    house_obj = await db_session.get(House, house.id)
    db_session.add(Item(house_id=house.id, container_id=container.id, status="confirmed",
                        item_type="single", name="Monitor LG 27", created_by=house_obj.created_by))
    db_session.add(Item(house_id=house.id, container_id=container.id, status="confirmed",
                        item_type="single", name="Tastiera Keychron", created_by=house_obj.created_by))
    await db_session.commit()

    resp = await client.get(f"/api/houses/{house.id}/items?search=monitor")
    assert resp.status_code == 200
    assert resp.json()["total"] == 1
    assert "Monitor" in resp.json()["items"][0]["name"]


# ── Inbox ─────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_inbox_groups_by_container(db_session: AsyncSession, item_client):
    client, house, container = item_client

    house_obj = await db_session.get(House, house.id)
    for _ in range(2):
        db_session.add(Item(house_id=house.id, container_id=container.id, status="draft_ai_done",
                            item_type="single", name="item", created_by=house_obj.created_by))
    await db_session.commit()

    resp = await client.get(f"/api/houses/{house.id}/inbox")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2
    assert data["ready_for_review"] >= 2
    assert len(data["by_container"]) >= 1
    group = next(g for g in data["by_container"] if g["container_id"] == container.id)
    assert len(group["items"]) >= 2


@pytest.mark.asyncio
async def test_inbox_counts_statuses(db_session: AsyncSession, item_client):
    client, house, container = item_client

    house_obj = await db_session.get(House, house.id)
    for s in ("draft", "draft_ai_done", "draft_ai_failed"):
        db_session.add(Item(house_id=house.id, container_id=container.id, status=s,
                            item_type="single", name=f"item_{s}", created_by=house_obj.created_by))
    await db_session.commit()

    resp = await client.get(f"/api/houses/{house.id}/inbox")
    data = resp.json()
    assert data["pending_ai"] >= 1
    assert data["ready_for_review"] >= 1
    assert data["failed"] >= 1


# ── Categories ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_and_list_categories(item_client):
    client, house, _ = item_client

    resp = await client.post(f"/api/houses/{house.id}/categories", json={"name": "Elettronica", "icon": "💻"})
    assert resp.status_code == 201
    assert resp.json()["name"] == "Elettronica"

    list_resp = await client.get(f"/api/houses/{house.id}/categories")
    assert list_resp.status_code == 200
    names = [c["name"] for c in list_resp.json()]
    assert "Elettronica" in names


@pytest.mark.asyncio
async def test_delete_category(item_client):
    client, house, _ = item_client
    created = (await client.post(f"/api/houses/{house.id}/categories", json={"name": "Temp"})).json()
    resp = await client.delete(f"/api/houses/{house.id}/categories/{created['id']}")
    assert resp.status_code == 204
