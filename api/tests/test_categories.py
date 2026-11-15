from app.models import Category
from tests.conftest import auth, make_course


async def test_student_cannot_create_category(client, student):
    resp = await client.post(
        "/categories/", json={"name": "Programiranje"}, headers=auth(student)
    )
    assert resp.status_code == 403
    assert resp.json()["code"] == "forbidden"


async def test_category_with_courses_cannot_be_deleted(client, db, admin, trainer):
    category = Category(name="Programiranje")
    db.add(category)
    await db.commit()
    course = await make_course(db, trainer)
    course.category_id = category.id
    await db.commit()

    resp = await client.delete(f"/categories/{category.id}", headers=auth(admin))
    assert resp.status_code == 409
    assert resp.json()["code"] == "category_has_courses"
