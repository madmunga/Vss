"""Critical: verify that author_id and real_name NEVER appear in any public API response."""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.community import Community


async def _register_and_token(client: AsyncClient, email: str) -> str:
    resp = await client.post("/auth/register", json={
        "email": email,
        "password": "Secure123",
        "addiction_types": ["ALCOHOL"],
    })
    assert resp.status_code == 201, resp.text
    return resp.json()["access_token"]


async def _seed_community(db: AsyncSession, slug: str, name: str, addiction_type: str = "ALCOHOL"):
    c = Community(name=name, slug=slug, addiction_type=addiction_type)
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c


@pytest.mark.asyncio
async def test_post_response_has_no_author_id(client: AsyncClient, db_session: AsyncSession):
    token = await _register_and_token(client, "privacy1@example.com")
    community = await _seed_community(db_session, "priv-com", "Privacy Test Community")

    await client.post("/communities/priv-com/join", headers={"Authorization": f"Bearer {token}"})

    post_resp = await client.post(
        "/posts",
        json={"community_id": str(community.id), "content": "This is my confession"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert post_resp.status_code == 201, post_resp.text

    post_data = post_resp.json()
    assert "author_id" not in post_data, "author_id must NEVER be in post response"
    assert "real_name" not in post_data, "real_name must NEVER be in post response"
    assert "email" not in post_data, "email must NEVER be in post response"
    assert "display_name" in post_data


@pytest.mark.asyncio
async def test_feed_has_no_author_id(client: AsyncClient, db_session: AsyncSession):
    token = await _register_and_token(client, "privacy2@example.com")
    community = await _seed_community(db_session, "feed-priv", "Feed Privacy Community", "DRUGS")

    await client.post("/communities/feed-priv/join", headers={"Authorization": f"Bearer {token}"})
    await client.post(
        "/posts",
        json={"community_id": str(community.id), "content": "Private confession"},
        headers={"Authorization": f"Bearer {token}"},
    )

    feed = await client.get("/posts", params={"community": "feed-priv"})
    assert feed.status_code == 200
    for post in feed.json()["posts"]:
        assert "author_id" not in post
        assert "real_name" not in post
        assert "email" not in post


@pytest.mark.asyncio
async def test_users_me_returns_real_info_only_to_owner(client: AsyncClient):
    """Only the authenticated user gets their own real email — no other endpoint returns it."""
    token = await _register_and_token(client, "realinfo@example.com")
    me = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    data = me.json()
    assert data["email"] == "realinfo@example.com"
    assert "display_name" in data
    # Professionals listing must not expose email
    professionals = await client.get("/professionals")
    assert professionals.status_code == 200
    for p in professionals.json():
        assert "email" not in p
        assert "real_name" not in p
