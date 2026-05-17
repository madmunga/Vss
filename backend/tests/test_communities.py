"""Tests: community listing, join/leave, tier gating."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import Community
from app.models.subscription import Subscription


async def _register_login(client: AsyncClient, email: str) -> str:
    resp = await client.post("/auth/register", json={
        "email": email, "password": "Secure123", "addiction_types": [],
    })
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


async def _seed_community(db: AsyncSession, slug: str, name: str, required_tier=None):
    c = Community(name=name, slug=slug, addiction_type="ALCOHOL", required_tier=required_tier)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@pytest.mark.asyncio
async def test_list_communities_public(client: AsyncClient, db_session: AsyncSession):
    await _seed_community(db_session, "pub-comm", "Public Community")
    resp = await client.get("/communities")
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1


@pytest.mark.asyncio
async def test_join_and_leave_community(client: AsyncClient, db_session: AsyncSession):
    token = await _register_login(client, "joiner@example.com")
    await _seed_community(db_session, "join-test", "Join Test Community")

    join = await client.post("/communities/join-test/join", headers={"Authorization": f"Bearer {token}"})
    assert join.status_code == 204

    leave = await client.delete("/communities/join-test/leave", headers={"Authorization": f"Bearer {token}"})
    assert leave.status_code == 204


@pytest.mark.asyncio
async def test_join_idempotent(client: AsyncClient, db_session: AsyncSession):
    token = await _register_login(client, "idempotent@example.com")
    await _seed_community(db_session, "idem-test", "Idempotent Test")

    await client.post("/communities/idem-test/join", headers={"Authorization": f"Bearer {token}"})
    resp = await client.post("/communities/idem-test/join", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 204  # idempotent — no error on re-join


@pytest.mark.asyncio
async def test_tier_gated_community_blocks_unsubscribed(client: AsyncClient, db_session: AsyncSession):
    token = await _register_login(client, "notsub@example.com")
    await _seed_community(db_session, "gated-s", "Gated S Community", required_tier="S")

    resp = await client.post("/communities/gated-s/join", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_community_not_found_returns_404(client: AsyncClient):
    resp = await client.get("/communities/does-not-exist")
    assert resp.status_code == 404
