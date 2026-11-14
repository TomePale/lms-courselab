from tests.conftest import auth, make_user

NEW_USER = {
    "email": "Novi.Trener@Test.hr",
    "password": "lozinka123",
    "first_name": "Novi",
    "last_name": "Trener",
    "role": "trainer",
}


async def test_student_and_trainer_get_403_on_users(client, student, trainer):
    for user in (student, trainer):
        resp = await client.get("/users/", headers=auth(user))
        assert resp.status_code == 403
        assert resp.json()["code"] == "forbidden"


async def test_users_without_token_is_401(client):
    resp = await client.get("/users/")
    assert resp.status_code == 401


async def test_deactivated_user_cannot_use_existing_token(client, admin, trainer):
    headers = auth(trainer)
    await client.patch(f"/users/{trainer.id}", json={"is_active": False}, headers=auth(admin))
    resp = await client.get("/auth/me", headers=headers)
    assert resp.status_code == 401
    assert resp.json()["code"] == "invalid_credentials"


async def test_pagination_slice_and_total(client, db, admin):
    for i in range(5):
        await make_user(db, f"s{i}@test.hr", "student")
    resp = await client.get("/users/?limit=2&offset=2", headers=auth(admin))
    body = resp.json()
    assert resp.status_code == 200
    # admin je id 1, studenti 2-6; sortirano po id-u, pa je isječak predvidljiv
    assert [u["email"] for u in body["items"]] == ["s1@test.hr", "s2@test.hr"]
    assert body["total"] == 6
    assert body["limit"] == 2 and body["offset"] == 2


async def test_limit_above_100_is_422(client, admin):
    resp = await client.get("/users/?limit=101", headers=auth(admin))
    assert resp.status_code == 422
    assert resp.json()["errors"][0]["field"] == "limit"
