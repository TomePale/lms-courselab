from tests.conftest import auth, make_course

COURSE_BODY = {
    "title": "Uvod u Python",
    "description": "Osnove programiranja",
    "capacity": 2,
    "enrollment_deadline": "2030-03-01T00:00:00Z",
    "start_date": "2030-03-10T00:00:00Z",
    "end_date": "2030-04-10T00:00:00Z",
}


# --- Stvaranje ---------------------------------------------------------------


async def test_student_cannot_create_course(client, student):
    resp = await client.post("/courses/", json=COURSE_BODY, headers=auth(student))
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"


async def test_invalid_date_order_on_create(client, trainer):
    body = {**COURSE_BODY, "start_date": "2030-05-01T00:00:00Z"}  # nakon end_date
    resp = await client.post("/courses/", json=body, headers=auth(trainer))
    assert resp.status_code == 400
    assert resp.json()["code"] == "invalid_dates"


# --- Vlasništvo i vidljivost ------------------------------------------------


async def test_trainer_cannot_edit_or_publish_foreign_course(client, db, trainer, trainer2):
    course = await make_course(db, trainer, status="draft")
    patch = await client.patch(
        f"/courses/{course.id}", json={"title": "Moje"}, headers=auth(trainer2)
    )
    publish = await client.post(f"/courses/{course.id}/publish", headers=auth(trainer2))
    assert patch.status_code == publish.status_code == 403


async def test_admin_can_edit_and_publish_any_course(client, db, admin, trainer):
    course = await make_course(db, trainer, status="draft")
    patch = await client.patch(
        f"/courses/{course.id}", json={"capacity": 20}, headers=auth(admin)
    )
    publish = await client.post(f"/courses/{course.id}/publish", headers=auth(admin))
    assert patch.status_code == publish.status_code == 200
    assert publish.json()["capacity"] == 20
    assert publish.json()["status"] == "published"


async def test_draft_visible_only_to_owner_and_admin(
    client, db, admin, trainer, trainer2, student
):
    course = await make_course(db, trainer, status="draft")
    url = f"/courses/{course.id}"
    assert (await client.get(url, headers=auth(trainer))).status_code == 200
    assert (await client.get(url, headers=auth(admin))).status_code == 200
    assert (await client.get(url, headers=auth(trainer2))).status_code == 404
    assert (await client.get(url, headers=auth(student))).status_code == 404


# --- Prijelazi statusa ------------------------------------------------------


async def test_invalid_course_transitions(client, db, trainer):
    draft = await make_course(db, trainer, status="draft", title="D")
    published = await make_course(db, trainer, status="published", title="P")
    archived = await make_course(db, trainer, status="archived", title="A")
    cases = [
        (draft, "archive"),
        (published, "publish"),
        (archived, "publish"),
        (archived, "archive"),
    ]
    for course, action in cases:
        resp = await client.post(f"/courses/{course.id}/{action}", headers=auth(trainer))
        assert resp.status_code == 400, (course.status, action)
        assert resp.json()["code"] == "invalid_status_transition"
