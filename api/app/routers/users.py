from fastapi import APIRouter, Depends, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import PageParams, get_db, get_page_params, require_role
from app.schemas.common import Page
from app.schemas.user import PasswordReset, Role, UserCreate, UserRead, UserUpdate
from app.services import user_service

# Sve rute ovog routera smije samo admin: ovisnost na razini routera
router = APIRouter(
    prefix="/users",
    tags=["users"],
    dependencies=[Depends(require_role("admin"))],
)


@router.get("/", response_model=Page[UserRead])
async def list_users(
    role: Role | None = Query(default=None),
    page: PageParams = Depends(get_page_params),
    db: AsyncSession = Depends(get_db),
):
    items, total = await user_service.list_users(db, role, page.limit, page.offset)
    return {"items": items, "total": total, "limit": page.limit, "offset": page.offset}


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, body)


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user_or_404(db, user_id)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: int, body: UserUpdate, db: AsyncSession = Depends(get_db)
):
    return await user_service.update_user(db, user_id, body)


@router.post("/{user_id}/reset-password", status_code=204)
async def reset_password(
    user_id: int, body: PasswordReset, db: AsyncSession = Depends(get_db)
):
    await user_service.reset_password(db, user_id, body.password)
    return Response(status_code=204)
