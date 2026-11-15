from tests.conftest import auth

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
