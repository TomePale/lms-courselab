"""Zajednička testna infrastruktura.

Testovi rade nad zasebnom bazom (TEST_DATABASE_URL), pa razvojni podaci
ostaju netaknuti. Shema se stvara migracijama, pa testovi provjeravaju i njih.
Prije pokretanja: docker compose up -d db
"""

import asyncio
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from pathlib import Path

import bcrypt
import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.deps import get_db
from app.core.jwt import create_access_token
from app.main import create_app
from app.models import Base, Course, User

TEST_DATABASE_URL = settings.TEST_DATABASE_URL

# NullPool: svaki test ima svoju petlju događaja, pa veze ne smiju preživjeti test
engine = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
TestSessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def _create_database_if_missing() -> None:
    url = make_url(TEST_DATABASE_URL)
    # Bazu ne možemo stvoriti iz nje same, pa se spajamo na sistemsku "postgres"
    server = create_async_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT", poolclass=NullPool
    )
    async with server.connect() as conn:
        exists = await conn.scalar(
            text("SELECT 1 FROM pg_database WHERE datname = :name"),
            {"name": url.database},
        )
        if not exists:
            await conn.execute(text(f'CREATE DATABASE "{url.database}"'))
    await server.dispose()


async def _drop_schema() -> None:
    # Brišemo sve, uključujući ENUM tipove i tablicu alembic_version
    async with engine.begin() as conn:
        await conn.execute(text("DROP SCHEMA public CASCADE"))
        await conn.execute(text("CREATE SCHEMA public"))


def _run_migrations() -> None:
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.set_main_option("sqlalchemy.url", TEST_DATABASE_URL)
    command.upgrade(config, "head")


@pytest.fixture(scope="session", autouse=True)
def test_database():
    """Jednom po pokretanju: prazna testna baza i shema iz migracija."""
    asyncio.run(_create_database_if_missing())
    asyncio.run(_drop_schema())
    _run_migrations()


@pytest.fixture(autouse=True)
async def clean_tables():
    """Svaki test počinje od praznih tablica."""
    tables = ", ".join(table.name for table in Base.metadata.sorted_tables)
    async with engine.begin() as conn:
        await conn.execute(text(f"TRUNCATE {tables} RESTART IDENTITY CASCADE"))


async def _get_test_db() -> AsyncGenerator[AsyncSession, None]:
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """HTTP klijent nad aplikacijom, bez pokretanja poslužitelja."""
    app = create_app()
    app.dependency_overrides[get_db] = _get_test_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Sesija za pripremu podataka izravno u bazi, mimo API-ja."""
    async with TestSessionLocal() as session:
        yield session


# --- Pomoćne funkcije i fixture za korisnike ---------------------------------


def fast_hash(password: str) -> str:
    # Faktor rada 4 umjesto zadanih 12: hash je jednako valjan, a testovi brži
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=4)).decode()


async def make_user(
    db: AsyncSession, email: str, role: str, password: str = "lozinka123"
) -> User:
    """Korisnik upisan izravno u bazu, mimo API-ja."""
    user = User(
        email=email,
        password_hash=fast_hash(password),
        first_name=email.split("@")[0].title(),
        last_name="Test",
        role=role,
    )
    db.add(user)
    await db.commit()
    return user


def auth(user: User) -> dict:
    """Zaglavlje s access tokenom za korisnika.

    Token se stvara pri pozivu, pa unutar freeze_time vrijedi za zamrznuto vrijeme.
    """
    return {"Authorization": f"Bearer {create_access_token(user.id, user.role)}"}


@pytest.fixture
async def admin(db: AsyncSession) -> User:
    return await make_user(db, "admin@test.hr", "admin")


@pytest.fixture
async def trainer(db: AsyncSession) -> User:
    return await make_user(db, "trener@test.hr", "trainer")


@pytest.fixture
async def student(db: AsyncSession) -> User:
    return await make_user(db, "student@test.hr", "student")


@pytest.fixture
async def trainer2(db: AsyncSession) -> User:
    """Drugi trener, za provjere vlasništva."""
    return await make_user(db, "trener2@test.hr", "trainer")


@pytest.fixture
async def student2(db: AsyncSession) -> User:
    """Drugi student, za provjere vlasništva."""
    return await make_user(db, "student2@test.hr", "student")


# --- Tečajevi ----------------------------------------------------------------

# Stalni datumi testnog tečaja. Testovi zamrzavaju vrijeme oko njih.
DEADLINE = datetime(2030, 3, 1, tzinfo=timezone.utc)
START = datetime(2030, 3, 10, tzinfo=timezone.utc)
END = datetime(2030, 4, 10, tzinfo=timezone.utc)

# Trenuci unutar svake faze, za freeze_time
DURING_OPEN = "2030-02-20 12:00:00"
DURING_CLOSED = "2030-03-05 12:00:00"
DURING_IN_PROGRESS = "2030-03-15 12:00:00"
DURING_FINISHED = "2030-04-15 12:00:00"


async def make_course(
    db: AsyncSession,
    trainer: User,
    status: str = "published",
    capacity: int = 10,
    title: str = "Test tečaj",
) -> Course:
    """Tečaj upisan izravno u bazu, mimo API-ja."""
    course = Course(
        trainer_id=trainer.id,
        title=title,
        capacity=capacity,
        enrollment_deadline=DEADLINE,
        start_date=START,
        end_date=END,
        status=status,
    )
    db.add(course)
    await db.commit()
    return course
