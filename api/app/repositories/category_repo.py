from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.category import Category
from app.models.course import Course


async def get_by_id(db: AsyncSession, category_id: int) -> Category | None:
    return await db.get(Category, category_id)


async def list_categories(
    db: AsyncSession, limit: int, offset: int
) -> tuple[list[Category], int]:
    stmt = select(Category)
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    # Abecedno po nazivu; id kao drugi ključ da poredak bude uvijek isti
    stmt = stmt.order_by(Category.name, Category.id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create(db: AsyncSession, category: Category) -> Category:
    db.add(category)
    await db.flush()
    return category


async def delete(db: AsyncSession, category: Category) -> None:
    await db.delete(category)
    await db.flush()


async def has_courses(db: AsyncSession, category_id: int) -> bool:
    """Koristi li ijedan tečaj ovu kategoriju."""
    stmt = select(Course.id).where(Course.category_id == category_id).limit(1)
    return await db.scalar(stmt) is not None
