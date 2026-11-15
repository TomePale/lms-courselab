import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.models.category import Category
from app.repositories import category_repo
from app.schemas.category import CategoryCreate, CategoryUpdate

logger = logging.getLogger(__name__)


async def get_category_or_404(db: AsyncSession, category_id: int) -> Category:
    category = await category_repo.get_by_id(db, category_id)
    if category is None:
        raise AppError("not_found", "Kategorija nije pronađena.", 404)
    return category


async def list_categories(
    db: AsyncSession, limit: int, offset: int
) -> tuple[list[Category], int]:
    return await category_repo.list_categories(db, limit, offset)


async def create_category(db: AsyncSession, body: CategoryCreate) -> Category:
    # Zauzet naziv odbija baza (uq_categories_name) -> 409 duplicate
    return await category_repo.create(db, Category(name=body.name))


async def update_category(
    db: AsyncSession, category_id: int, body: CategoryUpdate
) -> Category:
    category = await get_category_or_404(db, category_id)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    await db.flush()
    return category


async def delete_category(db: AsyncSession, category_id: int) -> None:
    category = await get_category_or_404(db, category_id)
    # Tečajevi bi ostali bez kategorije; baza bi brisanje ionako odbila (RESTRICT)
    if await category_repo.has_courses(db, category.id):
        raise AppError(
            "category_has_courses",
            "Kategoriju koriste tečajevi, pa se ne može obrisati.",
            409,
        )
    await category_repo.delete(db, category)
    logger.info("category deleted: id=%s", category_id)
