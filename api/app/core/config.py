from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# .env stoji u korijenu repozitorija: api/app/core/config.py -> parents[3]
ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


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

    # Varijabla okoline ima prednost pred vrijednošću iz .env datoteke
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")


settings = Settings()  # pyright: ignore[reportCallIssue]
