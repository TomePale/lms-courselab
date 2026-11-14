from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.security import hash_password
from app.models.user import User
from app.repositories import user_repo
from app.schemas.user import UserCreate, UserUpdate


async def get_user_or_404(db: AsyncSession, user_id: int) -> User:
    user = await user_repo.get_by_id(db, user_id)
    if user is None:
        raise AppError("not_found", "Korisnik nije pronađen.", 404)
    return user


async def list_users(
    db: AsyncSession, role: str | None, limit: int, offset: int
) -> tuple[list[User], int]:
    return await user_repo.list_users(db, role, limit, offset)


async def create_user(db: AsyncSession, body: UserCreate) -> User:
    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        first_name=body.first_name,
        last_name=body.last_name,
        role=body.role,
    )
    # Zauzet email odbija baza (uq_users_email); handler vraća 409 duplicate
    return await user_repo.create(db, user)


async def update_user(db: AsyncSession, user_id: int, body: UserUpdate) -> User:
    user = await get_user_or_404(db, user_id)
    # exclude_unset: samo polja koja je klijent stvarno poslao
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(user, field, value)
    await db.flush()
    return user


async def reset_password(db: AsyncSession, user_id: int, password: str) -> None:
    user = await get_user_or_404(db, user_id)
    user.password_hash = hash_password(password)
    await db.flush()
