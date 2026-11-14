"""Početni podaci za razvoj i obranu.

Pokreće se iz mape api/, nakon alembic upgrade head:
    python -m app.seed

Smije se pokrenuti bilo koliko puta: što već postoji, ne stvara se ponovno.
"""

import asyncio

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models import User

ADMIN = ("admin@courselab.hr", "admin123", "Admin", "CourseLab")


async def get_or_create_user(
    session: AsyncSession,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    role: str,
) -> User:
    # Idempotentnost: prvo tražimo po jedinstvenom ključu (email)
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        user = User(
            email=email,
            password_hash=hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
        )
        session.add(user)
        # flush šalje INSERT odmah, pa user dobiva id prije commita
        await session.flush()
    return user


async def seed(session: AsyncSession) -> None:
    """Sav posao seeda; prima sesiju, pa ga testovi mogu pokrenuti nad testnom bazom."""
    email, password, first_name, last_name = ADMIN
    await get_or_create_user(session, email, password, first_name, last_name, "admin")


async def main() -> None:
    # Jedna transakcija: ili su svi retci upisani, ili nijedan
    async with AsyncSessionLocal() as session, session.begin():
        await seed(session)
    await engine.dispose()
    print("Seed gotov.")
    print(f"  admin: {ADMIN[0]} / {ADMIN[1]}")


if __name__ == "__main__":
    asyncio.run(main())
