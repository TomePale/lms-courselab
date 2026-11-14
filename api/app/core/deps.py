from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal

# Ovisnost koja pruža sesiju baze podataka za svaki zahtjev.
# yield session omogućava korištenje sesije unutar rute FastAPI-a,
# a nakon toga se commit-a ili rollback-a transakcija.
# Ako dođe do iznimke unutar rute, transakcija se poništava.
# Nakon što ruta završi, sesija se automatski zatvara.
# Ova funkcija se koristi kao ovisnost u FastAPI rutama putem Depends(get_db).


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Jedna sesija, a time i jedna transakcija, po zahtjevu.

    commit tek kad cijela obrada prođe; iznimka iz bilo kojeg sloja
    poništava sve što je zahtjev upisao.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
