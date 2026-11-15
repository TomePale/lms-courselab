"""Početni podaci za razvoj i obranu.

Pokreće se iz mape api/, nakon alembic upgrade head:
    python -m app.seed

Smije se pokrenuti bilo koliko puta: svaki zapis traži se po svom jedinstvenom
ključu i stvara samo ako ne postoji.

Datumi tečajeva računaju se od trenutka prvog pokretanja, pa je jedan tečaj
tada u fazi upisa, a drugi u tijeku.
"""

import asyncio
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core import clock
from app.core.database import AsyncSessionLocal, engine
from app.core.security import hash_password
from app.models import Course, Enrollment, User

# (email, lozinka, ime, prezime, uloga)
USERS = [
    ("admin@courselab.hr", "admin123", "Tome", "Perica", "admin"),
    ("trener@courselab.hr", "trener123", "Summamed", "Forte", "trainer"),
    ("student1@courselab.hr", "student123", "Lanena", "Biosjemenka", "student"),
    ("student2@courselab.hr", "student123", "Vuk", "Vuković", "student"),
    ("student3@courselab.hr", "student123", "Marko", "Marković", "student"),
    ("student4@courselab.hr", "student123", "Ana", "Anić", "student"),
]


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


async def get_or_create(session: AsyncSession, model, defaults=None, **lookup):
    """Vrati zapis koji odgovara lookup uvjetima ili ga stvori.

    lookup su stupci jedinstvenog ključa (npr. trener i naziv tečaja), a
    defaults ostala polja koja se postavljaju samo pri stvaranju.
    """
    result = await session.execute(select(model).filter_by(**lookup))
    obj = result.scalar_one_or_none()
    if obj is None:
        obj = model(**lookup, **(defaults or {}))
        session.add(obj)
        await session.flush()
    return obj


async def seed(session: AsyncSession) -> None:
    """Sav posao seeda; prima sesiju, pa ga testovi mogu pokrenuti nad testnom bazom."""
    now = clock.now()
    day = timedelta(days=1)

    users = {}
    for email, password, first_name, last_name, role in USERS:
        users[email] = await get_or_create_user(
            session, email, password, first_name, last_name, role
        )
    trainer = users["trener@courselab.hr"]
    student1 = users["student1@courselab.hr"]
    student2 = users["student2@courselab.hr"]
    student3 = users["student3@courselab.hr"]
    student4 = users["student4@courselab.hr"]

    # 1) Upisi otvoreni: student2 čeka odluku trenera
    python = await get_or_create(
        session,
        Course,
        trainer_id=trainer.id,
        title="Uvod u Python",
        defaults={
            "description": "Osnove programiranja u Pythonu.",
            "capacity": 3,
            "enrollment_deadline": now + 14 * day,
            "start_date": now + 21 * day,
            "end_date": now + 60 * day,
            "status": "published",
        },
    )
    await get_or_create(
        session, Enrollment, student_id=student2.id, course_id=python.id
    )

    # 2) Tečaj u tijeku: student1 je prihvaćen
    databases = await get_or_create(
        session,
        Course,
        trainer_id=trainer.id,
        title="Baze podataka",
        defaults={
            "description": "Relacijski model, SQL i normalizacija.",
            "capacity": 10,
            "enrollment_deadline": now - 20 * day,
            "start_date": now - 10 * day,
            "end_date": now + 30 * day,
            "status": "published",
        },
    )
    await get_or_create(
        session,
        Enrollment,
        student_id=student1.id,
        course_id=databases.id,
        defaults={"status": "accepted", "decided_at": now - 15 * day},
    )


async def main() -> None:
    # Jedna transakcija: ili su svi retci upisani, ili nijedan
    async with AsyncSessionLocal() as session, session.begin():
        await seed(session)
    await engine.dispose()
    print("Seed gotov. Testni računi:")
    for email, password, _, _, role in USERS:
        print(f"  {role:8} {email} / {password}")


if __name__ == "__main__":
    asyncio.run(main())