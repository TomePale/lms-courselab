from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.course import Course


async def get_by_id(db: AsyncSession, course_id: int) -> Course | None:
    return await db.get(Course, course_id)


async def list_courses(
    db: AsyncSession,
    *,
    published_only: bool,
    also_owned_by: int | None,
    limit: int,
    offset: int,
) -> tuple[list[Course], int]:
    """Repozitorij ne zna za uloge; servis mu kaže koje uvjete primijeniti.

    published_only: samo objavljeni tečajevi,
    also_owned_by: uz objavljene i svi tečajevi tog vlasnika (bilo kojeg statusa).
    """
    stmt = select(Course)
    if published_only:
        visible = Course.status == "published"
        if also_owned_by is not None:
            visible = or_(visible, Course.trainer_id == also_owned_by)
        stmt = stmt.where(visible)

    # Ukupan broj s istim uvjetima, ali bez limit/offset
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    stmt = stmt.order_by(Course.id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create(db: AsyncSession, course: Course) -> Course:
    db.add(course)
    await db.flush()
    return course


async def delete(db: AsyncSession, course: Course) -> None:
    await db.delete(course)
    await db.flush()


async def lock_by_id(db: AsyncSession, course_id: int) -> Course | None:
    """SELECT ... FOR UPDATE: zaključava redak tečaja do kraja transakcije.

    Drugi zahtjev koji zaključava isti tečaj čeka dok prvi ne završi, pa dva
    istodobna prihvaćanja ne mogu oba vidjeti "ima još jedno mjesto".
    populate_existing osvježava objekt koji je možda već učitan u sesiju.
    """
    stmt = (
        select(Course)
        .where(Course.id == course_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    )
    result = await db.execute(stmt)
    return result.scalar_one_or_none()