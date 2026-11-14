from datetime import datetime

from pydantic import BaseModel, computed_field

from app.core import clock
from app.core.phases import CoursePhase, compute_phase


class CourseRead(BaseModel):
    id: int
    trainer_id: int
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