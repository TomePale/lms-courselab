import multiprocessing
import os
import signal
import sys
from pathlib import Path

from pydantic import ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# .env stoji u korijenu repozitorija: api/app/core/config.py -> parents[3]
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"

# Vrijednost iz .env.example; nije tajna jer je javno u repozitoriju
PLACEHOLDER_SECRET = "promijeni-me"


class Settings(BaseSettings):
    APP_NAME: str = "CourseLab API"
    ENV: str = "dev"

    # Bez zadane vrijednosti: ako varijabla nedostaje, aplikacija se ne pokreće
    DATABASE_URL: str
    TEST_DATABASE_URL: str
    JWT_SECRET_KEY: str

    JWT_ISSUER: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    @field_validator("JWT_SECRET_KEY")
    @classmethod
    def secret_key_must_be_real(cls, value: str) -> str:
        # S predloškom iz repozitorija svatko bi mogao potpisati valjan token,
        # npr. s ulogom admin. Zato se aplikacija s njim ne pokreće.
        if value == PLACEHOLDER_SECRET or len(value) < 32:
            raise ValueError(
                "mora biti vlastiti ključ od barem 32 znaka. "
                "Generiraj ga s: python -c "
                '"import secrets; print(secrets.token_hex(32))"'
            )
        return value

    # Varijabla okoline ima prednost pred vrijednošću iz .env datoteke
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


def load_settings() -> Settings:
    """Učitava postavke iz .env i okoline.

    Kod neispravne konfiguracije ispiše kratak popis problema i zaustavi
    program, umjesto dugog tracebacka u kojem se prava poruka izgubi.
    """
    try:
        # Vrijednosti dolaze iz .env pri pokretanju; Pylance to ne vidi
        # i misli da argumenti nedostaju
        return Settings()  # pyright: ignore[reportCallIssue]
    except ValidationError as exc:
        lines = [f"Neispravna konfiguracija ({ENV_FILE}):"]
        for err in exc.errors():
            field = ".".join(str(part) for part in err["loc"])
            if err["type"] == "missing":
                message = "nedostaje; dodaj ga u .env (vidi .env.example)"
            else:
                message = err["msg"].removeprefix("Value error, ")
            lines.append(f"  - {field}: {message}")
        print("\n".join(lines), file=sys.stderr)

        # Uz `uvicorn --reload` aplikacija se učitava u podprocesu, a nadzorni
        # proces bi i dalje čekao promjene datoteka. Gasimo i njega, da se
        # terminal oslobodi i ključ se može odmah generirati.
        parent = multiprocessing.parent_process()
        if parent is not None and parent.pid is not None:
            os.kill(parent.pid, signal.SIGTERM)

        # Izlaz s kodom 1, bez tracebacka
        sys.exit(1)


settings = load_settings()
