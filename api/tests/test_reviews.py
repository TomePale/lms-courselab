from freezegun import freeze_time

from tests.conftest import (
    DURING_FINISHED,
    DURING_IN_PROGRESS,
    auth,
    make_course,
    make_enrollment,
)

REVIEW = {"rating": 5, "comment": "Odličan tečaj"}


async def test_review_before_course_end_is_400(client, db, trainer, student):
    course = await make_course(db, trainer)
    await make_enrollment(db, student, course, status="accepted")
    with freeze_time(DURING_IN_PROGRESS):
        resp = await client.post(
            f"/courses/{course.id}/reviews/", json=REVIEW, headers=auth(student)
        )
    assert resp.status_code == 400
    assert resp.json()["code"] == "course_not_finished"


async def test_accepted_student_reviews_finished_course(client, db, trainer, student):
    course = await make_course(db, trainer)
    await make_enrollment(db, student, course, status="accepted")
    with freeze_time(DURING_FINISHED):
        resp = await client.post(
            f"/courses/{course.id}/reviews/", json=REVIEW, headers=auth(student)
        )
    assert resp.status_code == 201
    assert resp.json()["rating"] == 5
    assert resp.json()["student"]["id"] == student.id


async def test_pending_student_cannot_review(client, db, trainer, student):
    course = await make_course(db, trainer)
    await make_enrollment(db, student, course, status="pending")
    with freeze_time(DURING_FINISHED):
        resp = await client.post(
            f"/courses/{course.id}/reviews/", json=REVIEW, headers=auth(student)
        )
    assert resp.status_code == 403
    assert resp.json()["code"] == "not_enrolled"


async def test_second_review_is_409(client, db, trainer, student):
    course = await make_course(db, trainer)
    await make_enrollment(db, student, course, status="accepted")
    url = f"/courses/{course.id}/reviews/"
    with freeze_time(DURING_FINISHED):
        await client.post(url, json=REVIEW, headers=auth(student))
        resp = await client.post(url, json=REVIEW, headers=auth(student))
    assert resp.status_code == 409
    assert resp.json()["code"] == "duplicate"
