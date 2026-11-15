from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.enrollment import Enrollment

# Odgovor sadrži studenta i tečaj, pa ih učitavamo unaprijed. selectinload:
# jedan upit za upise i po jedan za sve njihove studente i tečajeve, umjesto
# jednog upita po upisu (problem N+1). U async načinu lijeno učitavanje ionako
# ne radi: pristup neučitanoj vezi baca iznimku.
LOAD_RELATED = (selectinload(Enrollment.student), selectinload(Enrollment.course))


async def get_by_id(db: AsyncSession, enrollment_id: int) -> Enrollment | None:
    stmt = select(Enrollment).options(*LOAD_RELATED).where(Enrollment.id == enrollment_id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def _paginate(stmt, db: AsyncSession, limit: int, offset: int):
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.options(*LOAD_RELATED).order_by(Enrollment.id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def list_for_course(
    db: AsyncSession, course_id: int, limit: int, offset: int
) -> tuple[list[Enrollment], int]:
    stmt = select(Enrollment).where(Enrollment.course_id == course_id)
    return await _paginate(stmt, db, limit, offset)


async def list_for_student(
    db: AsyncSession, student_id: int, limit: int, offset: int
) -> tuple[list[Enrollment], int]:
    stmt = select(Enrollment).where(Enrollment.student_id == student_id)
    return await _paginate(stmt, db, limit, offset)


async def create(db: AsyncSession, enrollment: Enrollment) -> Enrollment:
    db.add(enrollment)
    await db.flush()
    return enrollment


async def exists_for_course(db: AsyncSession, course_id: int) -> bool:
    """Ima li tečaj ijedan upis, bilo kojeg statusa."""
    stmt = select(Enrollment.id).where(Enrollment.course_id == course_id).limit(1)
    return await db.scalar(stmt) is not None

async def count_accepted(db: AsyncSession, course_id: int) -> int:
    """Broj zauzetih mjesta na tečaju: prihvaćeni upisi."""
    stmt = select(func.count(Enrollment.id)).where(
        Enrollment.course_id == course_id, Enrollment.status == "accepted"
    )
    return await db.scalar(stmt)
