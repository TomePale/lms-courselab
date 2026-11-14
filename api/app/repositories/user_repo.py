from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


async def get_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def list_users(
    db: AsyncSession, role: str | None, limit: int, offset: int
) -> tuple[list[User], int]:
    stmt = select(User)
    if role is not None:
        stmt = stmt.where(User.role == role)
    # Ukupan broj s istim filtrima, ali bez limit/offset
    total = await db.scalar(select(func.count()).select_from(stmt.subquery()))
    # Uvijek sortirano: bez ORDER BY baza ne jamči redoslijed,
    # pa bi se zapisi mogli ponoviti ili preskočiti između stranica
    stmt = stmt.order_by(User.id).limit(limit).offset(offset)
    result = await db.execute(stmt)
    return list(result.scalars().all()), total


async def create(db: AsyncSession, user: User) -> User:
    db.add(user)
    # flush šalje INSERT odmah: dobivamo id, a kršenje UNIQUE javlja se ovdje
    await db.flush()
    return user
