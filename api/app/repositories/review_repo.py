from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.review import Review


async def list_for_course(
    db: AsyncSession, course_id: int, limit: int, offset: int
) -> tuple[list[Review], int]:
    stmt = select(Review).where(Review.course_id == course_id)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    # Odgovor sadrži autora, pa ga učitavamo unaprijed (bez N+1 upita)
    stmt = (
        stmt.options(selectinload(Review.student))
        .order_by(Review.id)
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create(db: AsyncSession, review: Review) -> Review:
    db.add(review)
    await db.flush()
    return review
