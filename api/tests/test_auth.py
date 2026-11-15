from datetime import datetime, timedelta, timezone

import jwt

from app.core.config import settings
from tests.conftest import auth


async def login(client, email, password):
    return await client.post("/auth/login", json={"email": email, "password": password})


async def test_login_success(client, admin):
    resp = await login(client, "admin@test.hr", "lozinka123")
    assert resp.status_code == 200
    body = resp.json()
    assert body["access_token"] and body["refresh_token"]
    assert body["token_type"] == "bearer"


async def test_wrong_password_and_unknown_email_give_identical_401(client, admin):
    wrong_password = await login(client, "admin@test.hr", "kriva")
    unknown_email = await login(client, "nema@test.hr", "lozinka123")
    assert wrong_password.status_code == unknown_email.status_code == 401
    # Isti odgovor do zadnjeg znaka: iz njega se ne vidi postoji li račun
    assert wrong_password.json() == unknown_email.json()
    assert wrong_password.json()["code"] == "invalid_credentials"


async def test_overlong_password_gives_401_not_500(client, admin):
    # bcrypt odbija više od 72 bajta; prijava mora vratiti isti 401, a ne 500
    resp = await login(client, "admin@test.hr", "č" * 40)  # 40 znakova = 80 bajtova
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_me_without_token_is_401(client):
    resp = await client.get("/auth/me")
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_refresh_returns_new_pair(client, admin):
    tokens = (await login(client, "admin@test.hr", "lozinka123")).json()
    resp = await client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert resp.status_code == 200
    assert resp.json()["access_token"] and resp.json()["refresh_token"]


async def test_expired_token_returns_token_expired(client, admin):
    # Token potpisan ispravnim ključem, ali s istekom u prošlosti
    payload = {
        "sub": str(admin.id),
        "role": admin.role,
        "type": "access",
        "iss": settings.JWT_ISSUER,
        "exp": datetime.now(timezone.utc) - timedelta(minutes=1),
    }
    token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm="HS256")
    resp = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 401
    assert resp.json()["code"] == "token_expired"


async def test_user_changes_own_password(client, student):
    resp = await client.post(
        "/auth/change-password",
        json={"current_password": "lozinka123", "new_password": "nova-lozinka1"},
        headers=auth(student),
    )
    assert resp.status_code == 204
    old = await login(client, student.email, "lozinka123")
    new = await login(client, student.email, "nova-lozinka1")
    assert old.status_code == 401
    assert new.status_code == 200


async def test_change_password_requires_correct_current_password(client, student):
    resp = await client.post(
        "/auth/change-password",
        json={"current_password": "kriva-lozinka", "new_password": "nova-lozinka1"},
        headers=auth(student),
    )
    assert resp.status_code == 400
    assert resp.json()["code"] == "wrong_password"
