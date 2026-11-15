from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field, field_validator

from app.schemas.common import reject_null

Role = Literal["admin", "trainer", "student"]

# Jednostavna provjera oblika: nešto@nešto.nešto, bez razmaka.
# (EmailStr bi tražio dodatnu biblioteku email-validator.)
EMAIL_PATTERN = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


class UserCreate(BaseModel):
    email: str = Field(max_length=255, pattern=EMAIL_PATTERN, examples=["user@example.com"])
    # bcrypt uzima samo prva 72 bajta lozinke, pa dulje ne dopuštamo
    password: str = Field(min_length=8, max_length=72, examples=["user123"])
    first_name: str = Field(min_length=1, max_length=60)
    last_name: str = Field(min_length=1, max_length=60)
    role: Role

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserUpdate(BaseModel):
    # Sva polja opcionalna: PATCH mijenja samo poslano
    first_name: str | None = Field(default=None, min_length=1, max_length=60)
    last_name: str | None = Field(default=None, min_length=1, max_length=60)
    role: Role | None = None
    is_active: bool | None = None

    _not_null = field_validator("first_name", "last_name", "role", "is_active", mode="before")(
        reject_null
    )


class PasswordReset(BaseModel):
    password: str = Field(min_length=8, max_length=72)


class UserRead(BaseModel):
    # Eksplicitan popis polja: password_hash ovdje ne postoji, pa ne može
    # "procuriti" ni kad netko kasnije doda novi stupac u model
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    is_active: bool
    created_at: datetime

    # Izračunato polje: ne sprema se u bazu (bilo bi redundantno s imenom
    # i prezimenom), ali se pojavljuje u JSON odgovoru
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    # Dopušta UserRead.model_validate(user) iz SQLAlchemy objekta
    model_config = {"from_attributes": True}


class UserBrief(BaseModel):
    """Sažeti korisnik unutar drugih odgovora, npr. student u popisu upisa."""

    id: int
    first_name: str
    last_name: str
    email: str

    # Izračunato polje: ne sprema se u bazu (bilo bi redundantno s imenom
    # i prezimenom), ali se pojavljuje u JSON odgovoru
    @computed_field
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    model_config = {"from_attributes": True}
