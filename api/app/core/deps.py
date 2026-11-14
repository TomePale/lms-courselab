from collections.abc import AsyncGenerator
from dataclasses import dataclass

from fastapi import Depends, Query
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.errors import AppError
from app.core.jwt import ExpiredSignatureError, InvalidTokenError, decode_token
from app.models.user import User
from app.repositories import user_repo


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
    # 4) postoji li korisnik i je li aktivan: token opisuje stanje u trenutku
    #    izdavanja, a račun je u međuvremenu mogao biti deaktiviran
    user = await user_repo.get_by_id(db, int(payload["sub"]))
    if user is None or not user.is_active:
        raise AppError("invalid_credentials", "Neispravan token.", 401)
    return user


def require_role(*allowed_roles: str):
    """Stvara ovisnost koja propušta samo navedene uloge.

    Uloga se čita iz zapisa u bazi, a ne iz tokena, pa promjena uloge vrijedi odmah.
    """

    async def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise AppError("forbidden", "Nemate dozvolu za ovu radnju.", 403)
        return user

    return checker


@dataclass
class PageParams:
    limit: int
    offset: int


def get_page_params(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
) -> PageParams:
    """Parametri straničenja, isti za sve popise. limit=101 vraća 422."""
    return PageParams(limit=limit, offset=offset)
