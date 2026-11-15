from pydantic import BaseModel, Field, field_validator

from app.schemas.user import check_password_bytes


class LoginRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        # Email se u bazi sprema malim slovima, pa ga tako i tražimo
        return value.strip().lower()


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class ChangePasswordRequest(BaseModel):
    # Trenutna lozinka se samo provjerava, pa joj ne treba ograničenje duljine
    current_password: str
    new_password: str = Field(min_length=8, max_length=72)

    _password_bytes = field_validator("new_password")(check_password_bytes)
