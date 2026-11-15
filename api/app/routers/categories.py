from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import PageParams, get_current_user, get_db, get_page_params, require_role
from app.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate
from app.schemas.common import Page
from app.services import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


# Popis vidi svaki prijavljeni korisnik (treneru treba za odabir pri stvaranju tečaja)
@router.get("/", response_model=Page[CategoryRead], dependencies=[Depends(get_current_user)])
async def list_categories(
    page: PageParams = Depends(get_page_params),
    db: AsyncSession = Depends(get_db),
):
    items, total = await category_service.list_categories(db, page.limit, page.offset)
    return {"items": items, "total": total, "limit": page.limit, "offset": page.offset}


# Kategorijama upravlja samo admin
@router.post(
    "/",
    response_model=CategoryRead,
    status_code=201,
    dependencies=[Depends(require_role("admin"))],
)
async def create_category(body: CategoryCreate, db: AsyncSession = Depends(get_db)):
    return await category_service.create_category(db, body)


@router.patch(
    "/{category_id}",
    response_model=CategoryRead,
    dependencies=[Depends(require_role("admin"))],
)
async def update_category(
    category_id: int, body: CategoryUpdate, db: AsyncSession = Depends(get_db)
):
    return await category_service.update_category(db, category_id, body)


@router.delete(
    "/{category_id}", status_code=204, dependencies=[Depends(require_role("admin"))]
)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_db)):
    await category_service.delete_category(db, category_id)
