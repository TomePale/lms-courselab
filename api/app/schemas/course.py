from datetime import datetime

from pydantic import AwareDatetime, BaseModel, Field, computed_field, field_validator

from app.core import clock
from app.core.phases import CoursePhase, compute_phase
from app.schemas.common import reject_null


class CourseCreate(BaseModel):
    # Nema trainer_id: vlasnik tečaja je onaj tko ga stvori (iz tokena)
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    capacity: int = Field(gt=0)
    # AwareDatetime odbija vrijeme bez zone ("2026-12-01T10:00"): ne bi se znalo
    # je li to UTC ili lokalno vrijeme, a usporedba s now() ne bi bila moguća
    enrollment_deadline: AwareDatetime
    start_date: AwareDatetime
    end_date: AwareDatetime
    # Kategorija nije obavezna
    category_id: int | None = None


class CourseUpdate(BaseModel):
    # Datumi se zadaju pri stvaranju i ne mijenjaju se, pa ih ovdje nema
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    # Nije u reject_null: poslani null znači "makni kategoriju", jer je stupac
    # nullable. Izostavljeno polje i dalje znači "ne mijenjaj".
    category_id: int | None = None

    _not_null = field_validator("title", "description", "capacity", mode="before")(reject_null)


class CourseRead(BaseModel):
    id: int
    trainer_id: int
    category_id: int | None
    title: str
    description: str
    capacity: int
    enrollment_deadline: datetime
    start_date: datetime
    end_date: datetime
    status: str
    created_at: datetime

    # Izračunato polje: ne postoji u bazi, ali se pojavljuje u JSON odgovoru
    @computed_field
    @property
    def phase(self) -> CoursePhase:
        return compute_phase(self, clock.now())

    model_config = {"from_attributes": True}
