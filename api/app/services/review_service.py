from sqlalchemy.ext.asyncio import AsyncSession

from app.core import clock
from app.core.errors import AppError
from app.core.phases import CoursePhase, compute_phase
from app.models.review import Review
from app.models.user import User
from app.repositories import enrollment_repo, review_repo
from app.schemas.review import ReviewCreate
from app.services.course_service import get_visible_course


async def list_reviews(
    db: AsyncSession, course_id: int, user: User, limit: int, offset: int
) -> tuple[list[Review], int]:
    # Recenzije vidi svatko tko vidi i tečaj (tuđi nacrt -> 404)
    course = await get_visible_course(db, course_id, user)
    return await review_repo.list_for_course(db, course.id, limit, offset)


async def create_review(
    db: AsyncSession, course_id: int, body: ReviewCreate, user: User
) -> Review:
    course = await get_visible_course(db, course_id, user)
    # Ocjenjuje samo onaj tko je stvarno bio na tečaju
    if not await enrollment_repo.is_accepted(db, user.id, course.id):
        raise AppError(
            "not_enrolled", "Recenziju pišu samo studenti prihvaćeni na tečaj.", 403
        )
    # Tek kad je tečaj gotov, student zna kakav je bio
    if compute_phase(course, clock.now()) != CoursePhase.FINISHED:
        raise AppError("course_not_finished", "Tečaj još nije završio.", 400)
    # Druga recenzija istog studenta: odbija je baza (UNIQUE) -> 409 duplicate
    review = Review(
        course_id=course.id, student=user, rating=body.rating, comment=body.comment
    )
    return await review_repo.create(db, review)
