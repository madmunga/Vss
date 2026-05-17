"""Tests: registration, login, token refresh, email uniqueness, password validation."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_creates_user(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "email": "alice@example.com",
        "password": "Secure123",
        "real_name": "Alice Smith",
        "addiction_types": ["ALCOHOL"],
    })
    assert resp.status_code == 201
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_register_generates_pseudonym(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "bob@example.com",
        "password": "Secure123",
        "addiction_types": [],
    })
    me_resp = await client.get("/users/me", headers=_auth_headers(client, "bob@example.com", "Secure123"))
    # Login separately to get token
    login = await client.post("/auth/login", json={"email": "bob@example.com", "password": "Secure123"})
    token = login.json()["access_token"]
    me = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    display_name = me.json()["display_name"]
    assert "_" in display_name  # format: AdjectiveNoun_NNN
    assert display_name != ""


@pytest.mark.asyncio
async def test_register_duplicate_email_rejected(client: AsyncClient):
    payload = {"email": "dup@example.com", "password": "Secure123", "addiction_types": []}
    await client.post("/auth/register", json=payload)
    resp = await client.post("/auth/register", json=payload)
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_register_weak_password_rejected(client: AsyncClient):
    resp = await client.post("/auth/register", json={
        "email": "weak@example.com",
        "password": "short",
        "addiction_types": [],
    })
    assert resp.status_code == 409  # ValueError from auth_service


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "charlie@example.com",
        "password": "Secure123",
        "addiction_types": [],
    })
    resp = await client.post("/auth/login", json={"email": "charlie@example.com", "password": "Secure123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    await client.post("/auth/register", json={
        "email": "dan@example.com",
        "password": "Secure123",
        "addiction_types": [],
    })
    resp = await client.post("/auth/login", json={"email": "dan@example.com", "password": "WrongPass9"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_token_refresh(client: AsyncClient):
    reg = await client.post("/auth/register", json={
        "email": "eve@example.com",
        "password": "Secure123",
        "addiction_types": [],
    })
    refresh_token = reg.json()["refresh_token"]
    resp = await client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


@pytest.mark.asyncio
async def test_invalid_refresh_token_rejected(client: AsyncClient):
    resp = await client.post("/auth/refresh", json={"refresh_token": "not.a.valid.token"})
    assert resp.status_code == 401


def _auth_headers(client, email, password):
    """Helper — unused in tests above but kept for readability."""
    return {}
