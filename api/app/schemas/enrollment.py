from datetime import datetime

from pydantic import BaseModel

from app.schemas.user import UserBrief


class CourseBrief(BaseModel):
    """Sažeti tečaj unutar upisa: studentu u popisu "moji upisi" treba naziv."""

    id: int
    title: str
    description: str
    start_date: datetime
    end_date: datetime

    model_config = {"from_attributes": True}


class EnrollmentRead(BaseModel):
    # Nema EnrollmentCreate sa student_id: student se upisuje sam,
    # a id tečaja dolazi iz putanje. Status se mijenja samo radnjama.
    id: int
    student_id: int
    course_id: int
    status: str
    decided_at: datetime | None
    created_at: datetime
    student: UserBrief
    course: CourseBrief

    model_config = {"from_attributes": True}
