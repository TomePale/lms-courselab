from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, String, func, true
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.course import Course

# Dopuštene uloge. Baza ih provodi kao PostgreSQL ENUM tip user_role,
# pa ni upis iz konzole ne prolazi s ulogom "admn".
USER_ROLES = ("admin", "trainer", "student")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True uz naming convention daje ograničenje uq_users_email.
    # Email se sprema malim slovima (to radi shema), pa je jedinstvenost stvarna.
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(60), nullable=False)
    last_name: Mapped[str] = mapped_column(String(60), nullable=False)
    role: Mapped[str] = mapped_column(Enum(*USER_ROLES, name="user_role"), nullable=False)
    # Korisnici se ne brišu nego deaktiviraju: njihovi tečajevi, upisi i predaje
    # ostaju, a deaktiviran račun ne prolazi prijavu ni provjeru tokena
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=true()
    )
    # Vrijeme upisa daje baza, pa ne ovisi o satu poslužitelja
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Tečajevi kojima je korisnik trener (druga strana: Course.trainer)
    courses: Mapped[list["Course"]] = relationship(back_populates="trainer")
