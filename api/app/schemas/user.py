from datetime import datetime

from pydantic import BaseModel, computed_field


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
