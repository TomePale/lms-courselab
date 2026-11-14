from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.jwt import (
    ExpiredSignatureError,
    InvalidTokenError,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.core.security import hash_password, verify_password
from app.models.user import User
from app.repositories import user_repo
from app.schemas.auth import TokenPair

# Hash bez stvarnog korisnika. Kad email ne postoji, ipak provjeravamo lozinku
# prema njemu, pa odgovor traje jednako dugo kao za krivu lozinku i iz trajanja
# se ne može zaključiti postoji li račun.
DUMMY_HASH = hash_password("dummy-password")


def _invalid_credentials() -> AppError:
    # Uvijek ista poruka: klijent ne smije saznati je li kriv email ili lozinka
    return AppError("invalid_credentials", "Neispravan email ili lozinka.", 401)


def _token_pair(user: User) -> TokenPair:
    return TokenPair(
        access_token=create_access_token(user.id, user.role),
        refresh_token=create_refresh_token(user.id, user.role),
    )


async def login(db: AsyncSession, email: str, password: str) -> TokenPair:
    user = await user_repo.get_by_email(db, email)
    if user is None:
        verify_password(password, DUMMY_HASH)
        raise _invalid_credentials()
    if not verify_password(password, user.password_hash):
        raise _invalid_credentials()
    # Deaktiviran račun dobiva isti odgovor kao kriva lozinka
    if not user.is_active:
        raise _invalid_credentials()
    return _token_pair(user)


async def refresh(db: AsyncSession, refresh_token: str) -> TokenPair:
    try:
        payload = decode_token(refresh_token)
    except ExpiredSignatureError:
        raise AppError("token_expired", "Token je istekao.", 401)
    except InvalidTokenError:
        raise AppError("invalid_credentials", "Neispravan token.", 401)
    # Access token ovdje ne vrijedi: inače bi ukradeni access token
    # mogao beskonačno produljivati sesiju
    if payload["type"] != "refresh":
        raise AppError("invalid_credentials", "Neispravan token.", 401)

    user = await user_repo.get_by_id(db, int(payload["sub"]))
    if user is None or not user.is_active:
        raise AppError("invalid_credentials", "Neispravan token.", 401)
    return _token_pair(user)
