import asyncio

from freezegun import freeze_time

from tests.conftest import (
    DURING_CLOSED,
    DURING_OPEN,
    auth,
    make_course,
    make_enrollment,
    make_user,
)

# Rok upisa testnog tečaja je 2030-03-01 00:00:00 UTC
JUST_BEFORE_DEADLINE = "2030-02-28 23:59:59"
JUST_AFTER_DEADLINE = "2030-03-01 00:00:01"


# --- Upis --------------------------------------------------------------------


async def test_enroll_one_second_before_deadline(client, db, trainer, student):
    course = await make_course(db, trainer)
    with freeze_time(JUST_BEFORE_DEADLINE):
        resp = await client.post(
            f"/courses/{course.id}/enrollments/", headers=auth(student)
        )
    assert resp.status_code == 201
    assert resp.json()["status"] == "pending"
    assert resp.json()["student_id"] == student.id


async def test_enroll_one_second_after_deadline(client, db, trainer, student):
    course = await make_course(db, trainer)
    with freeze_time(JUST_AFTER_DEADLINE):
        resp = await client.post(
            f"/courses/{course.id}/enrollments/", headers=auth(student)
        )
    assert resp.status_code == 400
    assert resp.json()["code"] == "enrollment_closed"


async def test_double_enrollment_is_409(client, db, trainer, student):
    course = await make_course(db, trainer)
    with freeze_time(DURING_OPEN):
        url = f"/courses/{course.id}/enrollments/"
        await client.post(url, headers=auth(student))
        resp = await client.post(url, headers=auth(student))
    assert resp.status_code == 409
    assert resp.json()["code"] == "duplicate"


async def test_enroll_on_draft_course_is_400(client, db, trainer, student):
    course = await make_course(db, trainer, status="draft")
    with freeze_time(DURING_OPEN):
        resp = await client.post(
            f"/courses/{course.id}/enrollments/", headers=auth(student)
        )
    assert resp.status_code == 400
    assert resp.json()["code"] == "course_not_published"


async def test_trainer_cannot_enroll(client, db, trainer, trainer2):
    course = await make_course(db, trainer)
    with freeze_time(DURING_OPEN):
        resp = await client.post(
            f"/courses/{course.id}/enrollments/", headers=auth(trainer2)
        )
    assert resp.status_code == 403


# --- Vidljivost --------------------------------------------------------------


async def test_trainer_cannot_list_enrollments_of_foreign_course(
    client, db, trainer, trainer2
):
    course = await make_course(db, trainer)
    resp = await client.get(
        f"/courses/{course.id}/enrollments/", headers=auth(trainer2)
    )
    assert resp.status_code == 403


async def test_enrollment_visible_to_owner_and_course_trainer_only(
    client, db, admin, trainer, trainer2, student, student2
):
    course = await make_course(db, trainer)
    enrollment = await make_enrollment(db, student, course)
    url = f"/enrollments/{enrollment.id}"
    assert (await client.get(url, headers=auth(student))).status_code == 200
    assert (await client.get(url, headers=auth(trainer))).status_code == 200
    assert (await client.get(url, headers=auth(admin))).status_code == 200
    assert (await client.get(url, headers=auth(student2))).status_code == 403
    assert (await client.get(url, headers=auth(trainer2))).status_code == 403


async def test_my_enrollments_contain_only_own(client, db, trainer, student, student2):
    course = await make_course(db, trainer)
    await make_enrollment(db, student, course)
    await make_enrollment(db, student2, course)
    resp = await client.get("/me/enrollments/", headers=auth(student))
    assert resp.json()["total"] == 1
    assert resp.json()["items"][0]["course"]["title"] == "Test tečaj"


# --- Prihvaćanje i kapacitet -------------------------------------------------


async def test_accept_up_to_capacity_then_course_full(client, db, trainer):
    course = await make_course(db, trainer, capacity=2)
    enrollments = []
    for i in range(3):
        student = await make_user(db, f"s{i}@test.hr", "student")
        enrollments.append(await make_enrollment(db, student, course))

    with freeze_time(DURING_CLOSED):
        results = [
            await client.post(f"/enrollments/{e.id}/accept", headers=auth(trainer))
            for e in enrollments
        ]
    assert [r.status_code for r in results] == [200, 200, 409]
    assert results[0].json()["decided_at"] is not None
    assert results[2].json()["code"] == "course_full"


async def test_concurrent_acceptances_respect_capacity(client, db, trainer):
    # Dva prihvaćanja u istom trenutku, a mjesto je samo jedno.
    # SELECT ... FOR UPDATE tjera drugi zahtjev da pričeka prvi.
    course = await make_course(db, trainer, capacity=1)
    a = await make_enrollment(db, await make_user(db, "a@test.hr", "student"), course)
    b = await make_enrollment(db, await make_user(db, "b@test.hr", "student"), course)
    with freeze_time(DURING_OPEN):
        results = await asyncio.gather(
            client.post(f"/enrollments/{a.id}/accept", headers=auth(trainer)),
            client.post(f"/enrollments/{b.id}/accept", headers=auth(trainer)),
        )
    assert sorted(r.status_code for r in results) == [200, 409]


async def test_trainer_cannot_accept_on_foreign_course(
    client, db, trainer, trainer2, student
):
    course = await make_course(db, trainer)
    enrollment = await make_enrollment(db, student, course)
    resp = await client.post(
        f"/enrollments/{enrollment.id}/accept", headers=auth(trainer2)
    )
    assert resp.status_code == 403


async def test_admin_can_accept_on_any_course(client, db, admin, trainer, student):
    course = await make_course(db, trainer)
    enrollment = await make_enrollment(db, student, course)
    resp = await client.post(
        f"/enrollments/{enrollment.id}/accept", headers=auth(admin)
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "accepted"


async def test_only_pending_enrollment_can_be_decided(client, db, trainer, student):
    course = await make_course(db, trainer)
    cases = [
        ("accepted", "accept"),
        ("accepted", "reject"),
        ("rejected", "accept"),
        ("rejected", "reject"),
    ]
    for status, action in cases:
        enrollment = await make_enrollment(db, student, course, status)
        resp = await client.post(
            f"/enrollments/{enrollment.id}/{action}", headers=auth(trainer)
        )
        assert resp.status_code == 400, (status, action)
        assert resp.json()["code"] == "invalid_status_transition"
        # Isti student smije imati samo jedan upis na tečaj, pa ga brišemo
        await db.delete(enrollment)
        await db.commit()


async def test_course_with_enrollments_cannot_be_deleted(client, db, trainer, student):
    course = await make_course(db, trainer)
    with freeze_time(DURING_OPEN):
        await client.post(f"/courses/{course.id}/enrollments/", headers=auth(student))
    resp = await client.delete(f"/courses/{course.id}", headers=auth(trainer))
    assert resp.status_code == 409
    assert resp.json()["code"] == "course_has_enrollments"
