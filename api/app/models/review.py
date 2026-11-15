from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class Review(Base):
    """Recenzija tečaja: ocjena 1-5 i komentar studenta nakon završetka tečaja."""

    __tablename__ = "reviews"
    __table_args__ = (
        # Jedna recenzija po studentu i tečaju: uq_reviews_course_id_student_id.
        # course_id je prvi stupac, pa isti indeks služi i za popis recenzija tečaja.
        UniqueConstraint("course_id", "student_id"),
        # Raspon ocjene provodi i baza: ck_reviews_rating_range
        CheckConstraint("rating BETWEEN 1 AND 5", name="rating_range"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # RESTRICT: recenzija je povijesni zapis, ne nestaje usput s tečajem ni korisnikom
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False
    )
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False, default="", server_default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Samo u jednom smjeru: odgovor prikazuje autora recenzije
    student: Mapped["User"] = relationship()
