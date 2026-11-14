from collections.abc import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.errors import AppError
from app.core.jwt import ExpiredSignatureError, InvalidTokenError, decode_token
from app.models.user import User
from app.repositories import user_repo

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

# auto_error=False: bez zaglavlja dobivamo None i sami vraćamo 401 u našem obliku
_bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # 1) je li token uopće poslan
    if credentials is None:
        raise AppError("invalid_credentials", "Nedostaje token.", 401)
    # 2) može li se dekodirati: potpis, istek, izdavatelj
    try:
        payload = decode_token(credentials.credentials)
    except ExpiredSignatureError:
        raise AppError("token_expired", "Token je istekao.", 401)
    except InvalidTokenError:
        raise AppError("invalid_credentials", "Neispravan token.", 401)
    # 3) je li to access, a ne refresh token
    if payload["type"] != "access":
        raise AppError("invalid_credentials", "Neispravan token.", 401)
    # 4) postoji li korisnik još uvijek: token opisuje stanje u trenutku izdavanja
    user = await user_repo.get_by_id(db, int(payload["sub"]))
    if user is None:
        raise AppError("invalid_credentials", "Neispravan token.", 401)
    return user
