from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.enrollment import Enrollment
    from app.models.user import User

# Status je odluka trenera i sprema se u bazu (za razliku od faze, koja se računa)
COURSE_STATUSES = ("draft", "published", "archived")


class Course(Base):
    __tablename__ = "courses"
    __table_args__ = (
        # Ime "capacity_positive" uz naming convention postaje
        # ck_courses_capacity_positive
        CheckConstraint("capacity > 0", name="capacity_positive"),
        # Poredak datuma provodi i baza, kao zadnja zaštita iza provjere u servisu
        CheckConstraint(
            "enrollment_deadline <= start_date AND start_date < end_date",
            name="dates",
        ),
        # Isti trener ne može imati dva tečaja istog naziva; različiti treneri mogu.
        # Ime po naming conventionu: uq_courses_trainer_id_title
        UniqueConstraint("trainer_id", "title"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # RESTRICT: korisnik koji ima tečajeve ne može se obrisati,
    # pa tečaj nikad ne ostaje bez trenera
    trainer_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(
        Text, nullable=False, default="", server_default=""
    )
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    enrollment_deadline: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    start_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    # Indeks: gotovo svaki popis filtrira po statusu (student vidi samo published)
    status: Mapped[str] = mapped_column(
        Enum(*COURSE_STATUSES, name="course_status"),
        nullable=False,
        default="draft",
        server_default="draft",
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    trainer: Mapped["User"] = relationship(back_populates="courses")
    enrollments: Mapped[list["Enrollment"]] = relationship(back_populates="course")
