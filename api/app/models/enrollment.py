from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.course import Course
    from app.models.user import User

ENROLLMENT_STATUSES = ("pending", "accepted", "rejected")


class Enrollment(Base):
    """Upis studenta na tečaj: vezna tablica N:M veze users <-> courses,
    s vlastitim podacima (status, vrijeme odluke)."""

    __tablename__ = "enrollments"
    __table_args__ = (
        # Jedan upis po studentu i tečaju. Ovaj složeni indeks ujedno služi
        # i za traženje po student_id ("moji upisi").
        UniqueConstraint("student_id", "course_id"),
        # Popunjenost se broji upitom WHERE course_id = ? AND status = 'accepted'.
        # Složeni indeks pokriva oba uvjeta, a sam course_id i za popis upisa tečaja.
        Index("ix_enrollments_course_id_status", "course_id", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # RESTRICT: upis je povijesni zapis, ne smije nestati usput s korisnikom
    student_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    course_id: Mapped[int] = mapped_column(
        ForeignKey("courses.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(
        Enum(*ENROLLMENT_STATUSES, name="enrollment_status"),
        nullable=False,
        default="pending",
        server_default="pending",
    )
    # Kad je trener prihvatio ili odbio upis; NULL dok odluke nema
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    student: Mapped["User"] = relationship(back_populates="enrollments")
    course: Mapped["Course"] = relationship(back_populates="enrollments")
