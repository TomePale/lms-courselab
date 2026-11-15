from datetime import datetime

from pydantic import BaseModel, Field


class ReviewAuthor(BaseModel):
    """Autor recenzije bez emaila: recenzije čitaju svi koji vide tečaj."""

    id: int
    first_name: str
    last_name: str

    model_config = {"from_attributes": True}


class ReviewCreate(BaseModel):
    # Nema course_id ni student_id: tečaj je u putanji, a student iz tokena
    rating: int = Field(ge=1, le=5, examples=[5])
    comment: str = Field(default="", max_length=1000)


class ReviewRead(BaseModel):
    id: int
    course_id: int
    rating: int
    comment: str
    created_at: datetime
    student: ReviewAuthor

    model_config = {"from_attributes": True}
