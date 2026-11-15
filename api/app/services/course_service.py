from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.course import Course
from app.models.user import User
from app.repositories import course_repo, enrollment_repo
from app.schemas.course import CourseCreate, CourseUpdate

# --- Pomoćne funkcije koje koriste i drugi servisi --------------------------


async def get_course_or_404(db: AsyncSession, course_id: int) -> Course:
    course = await course_repo.get_by_id(db, course_id)
    if course is None:
        raise AppError("not_found", "Tečaj nije pronađen.", 404)
    return course


def can_manage(course: Course, user: User) -> bool:
    """Admin smije sve, a ostali samo tečajeve koje su sami stvorili."""
    return user.role == "admin" or course.trainer_id == user.id


def ensure_can_manage(course: Course, user: User) -> None:
    if not can_manage(course, user):
        raise AppError("forbidden", "Nemate ovlasti nad ovim tečajem.", 403)


def ensure_published(course: Course) -> None:
    """Upis traži objavljen tečaj."""
    if course.status != "published":
        raise AppError("course_not_published", "Tečaj nije objavljen.", 400)


# --- Radnje ------------------------------------------------------------------


async def list_courses(
    db: AsyncSession, user: User, limit: int, offset: int
) -> tuple[list[Course], int]:
    # Vidljivost ovisi o ulozi: admin sve, trener svoje i objavljene,
    # student samo objavljene. Filtriranje je u upitu, pa tuđi zapisi
    # ni ne izlaze iz baze.
    return await course_repo.list_courses(
        db,
        published_only=user.role != "admin",
        also_owned_by=user.id if user.role == "trainer" else None,
        limit=limit,
        offset=offset,
    )


async def get_visible_course(db: AsyncSession, course_id: int, user: User) -> Course:
    course = await get_course_or_404(db, course_id)
    # Neobjavljen tečaj vide samo vlasnik i admin. Ostali dobivaju 404, a ne 403,
    # pa iz odgovora ne mogu ni zaključiti da tečaj postoji.
    if course.status != "published" and not can_manage(course, user):
        raise AppError("not_found", "Tečaj nije pronađen.", 404)
    return course


async def create_course(db: AsyncSession, body: CourseCreate, user: User) -> Course:
    if not (body.enrollment_deadline <= body.start_date < body.end_date):
        raise AppError(
            "invalid_dates",
            "Mora vrijediti: rok upisa <= početak < kraj tečaja.",
            400,
        )
    # Vlasnik je onaj tko stvara tečaj: trener ili admin
    course = Course(trainer_id=user.id, **body.model_dump())
    # Isti naziv kod istog vlasnika odbija baza (UNIQUE) -> 409 duplicate
    return await course_repo.create(db, course)


async def update_course(
    db: AsyncSession, course_id: int, body: CourseUpdate, user: User
) -> Course:
    course = await get_course_or_404(db, course_id)
    ensure_can_manage(course, user)
    # exclude_unset: samo polja koja je klijent stvarno poslao
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(course, field, value)
    await db.flush()
    return course


# Dopušteni prijelazi statusa: iz kojeg stanja u koje. archived je završno stanje.
COURSE_TRANSITIONS = {
    "publish": ("draft", "published"),
    "archive": ("published", "archived"),
}


async def change_status(
    db: AsyncSession, course_id: int, action: str, user: User
) -> Course:
    course = await get_course_or_404(db, course_id)
    ensure_can_manage(course, user)
    from_status, to_status = COURSE_TRANSITIONS[action]
    if course.status != from_status:
        raise AppError(
            "invalid_status_transition",
            f"Prijelaz {course.status} -> {to_status} nije dopušten.",
            400,
        )
    course.status = to_status
    await db.flush()
    return course


async def delete_course(db: AsyncSession, course_id: int, user: User) -> None:
    """Brisati se smije tečaj na koji nitko nije upisan."""
    course = await get_course_or_404(db, course_id)
    ensure_can_manage(course, user)
    # Upisi su povijest (tko se prijavio, tko je prihvaćen). Takav tečaj
    # se arhivira; baza bi brisanje ionako odbila (RESTRICT).
    if await enrollment_repo.exists_for_course(db, course.id):
        raise AppError(
            "course_has_enrollments",
            "Tečaj ima upise, pa se ne može obrisati; arhivirajte ga.",
            409,
        )
    await course_repo.delete(db, course)
