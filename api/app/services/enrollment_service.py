import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core import clock
from app.core.errors import AppError
from app.core.phases import CoursePhase, compute_phase
from app.models.enrollment import Enrollment
from app.models.user import User
from app.repositories import course_repo, enrollment_repo
from app.services.course_service import (
    can_manage,
    ensure_can_manage,
    ensure_published,
    get_course_or_404,
)

logger = logging.getLogger(__name__)


async def _get_enrollment_or_404(db: AsyncSession, enrollment_id: int) -> Enrollment:
    enrollment = await enrollment_repo.get_by_id(db, enrollment_id)
    if enrollment is None:
        raise AppError("not_found", "Upis nije pronađen.", 404)
    return enrollment


# --- Čitanje -----------------------------------------------------------------


async def list_course_enrollments(
    db: AsyncSession, course_id: int, user: User, limit: int, offset: int
) -> tuple[list[Enrollment], int]:
    course = await get_course_or_404(db, course_id)
    ensure_can_manage(course, user)
    return await enrollment_repo.list_for_course(db, course_id, limit, offset)


async def list_my_enrollments(
    db: AsyncSession, user: User, limit: int, offset: int
) -> tuple[list[Enrollment], int]:
    # student_id dolazi iz tokena, ne iz zahtjeva: tuđi upisi nisu ni dohvatljivi
    return await enrollment_repo.list_for_student(db, user.id, limit, offset)


async def get_enrollment(db: AsyncSession, enrollment_id: int, user: User):
    enrollment = await _get_enrollment_or_404(db, enrollment_id)
    is_owner = enrollment.student_id == user.id
    if not is_owner and not can_manage(enrollment.course, user):
        raise AppError("forbidden", "Nemate pristup ovom upisu.", 403)
    return enrollment


# --- Upis --------------------------------------------------------------------


async def enroll(db: AsyncSession, course_id: int, user: User) -> Enrollment:
    course = await get_course_or_404(db, course_id)
    ensure_published(course)
    if compute_phase(course, clock.now()) != CoursePhase.ENROLLMENT_OPEN:
        raise AppError("enrollment_closed", "Rok za upis je prošao.", 400)
    # Drugi upis istog studenta odbija baza (UNIQUE) -> 409 duplicate.
    # Provjera "postoji li već" prije upisa ne bi bila dovoljna: dva istodobna
    # zahtjeva prošla bi je oba.
    enrollment = Enrollment(student=user, course=course)
    return await enrollment_repo.create(db, enrollment)


# --- Odluke vlasnika tečaja ili admina ----------------------------------------


async def _get_pending(
    db: AsyncSession, enrollment_id: int, user: User, target: str
) -> Enrollment:
    """Zajednički dio prihvaćanja i odbijanja: postojanje, ovlast i status."""
    enrollment = await _get_enrollment_or_404(db, enrollment_id)
    ensure_can_manage(enrollment.course, user)
    # Odlučuje se samo o upisu koji čeka; accepted i rejected su konačni
    if enrollment.status != "pending":
        raise AppError(
            "invalid_status_transition",
            f"Prijelaz {enrollment.status} -> {target} nije dopušten.",
            400,
        )
    return enrollment


async def accept(db: AsyncSession, enrollment_id: int, user: User) -> Enrollment:
    enrollment = await _get_pending(db, enrollment_id, user, "accepted")
    # Prvo zaključavamo tečaj, tek onda brojimo. Bez zaključavanja dva
    # istodobna zahtjeva oba izbroje 9/10 i oba prihvate: 11/10.
    course = await course_repo.lock_by_id(db, enrollment.course_id)
    taken = await enrollment_repo.count_accepted(db, course.id)
    if taken >= course.capacity:
        raise AppError("course_full", "Tečaj je popunjen.", 409)
    enrollment.status = "accepted"
    enrollment.decided_at = clock.now()
    await db.flush()
    logger.info("enrollment accepted: id=%s course_id=%s", enrollment.id, course.id)
    return enrollment


async def reject(db: AsyncSession, enrollment_id: int, user: User) -> Enrollment:
    enrollment = await _get_pending(db, enrollment_id, user, "rejected")
    enrollment.status = "rejected"
    enrollment.decided_at = clock.now()
    await db.flush()
    logger.info("enrollment rejected: id=%s", enrollment.id)
    return enrollment
