"""Zajednička testna infrastruktura.

Testovi rade nad zasebnom bazom (TEST_DATABASE_URL), pa razvojni podaci
ostaju netaknuti. Shema se stvara migracijama, pa testovi provjeravaju i njih.
Prije pokretanja: docker compose up -d db
"""

import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config
from httpx import ASGITransport, AsyncClient
from sqlalchemy import make_url, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.core.config import settings
from app.core.deps import get_db
from app.main import create_app
from app.models import Base

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
