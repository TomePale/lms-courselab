from datetime import timedelta

import jwt
from jwt import ExpiredSignatureError, InvalidTokenError

from app.core import clock
from app.core.config import settings

# Ponovno izvozimo iznimke da ostatak aplikacije ne uvozi izravno iz paketa jwt
__all__ = [
    "ExpiredSignatureError",
    "InvalidTokenError",
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]

ALGORITHM = "HS256"


def _create_token(user_id: int, role: str, token_type: str, lifetime: timedelta) -> str:
    now = clock.now()
    payload = {
        "sub": str(user_id),  # JWT standard traži da sub bude string
        "role": role,
        "type": token_type,  # "access" ili "refresh"
        "iss": settings.JWT_ISSUER,
        "exp": now + lifetime,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(user_id: int, role: str) -> str:
    """Kratkotrajan token koji putuje uz svaki zahtjev."""
    lifetime = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _create_token(user_id, role, "access", lifetime)


def create_refresh_token(user_id: int, role: str) -> str:
    """Dugotrajan token koji se šalje samo na /auth/refresh."""
    lifetime = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(user_id, role, "refresh", lifetime)


def decode_token(token: str) -> dict:
    """Provjerava potpis, istek i izdavatelja te vraća sadržaj tokena.

    Istekao token podiže ExpiredSignatureError, svaki drugi neispravan token
    InvalidTokenError. Prva je podvrsta druge, pa se uvijek hvata prva.
    """
    return jwt.decode(
        token,
        settings.JWT_SECRET_KEY,
        algorithms=[ALGORITHM],  # nikad algoritam iz zaglavlja samog tokena
        issuer=settings.JWT_ISSUER,
        options={"require": ["exp", "sub", "iss", "type"]},
    )
