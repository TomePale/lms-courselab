from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Jedna stranica popisa. total je ukupan broj zapisa, za izračun stranica."""

    items: list[T]
    total: int
    limit: int
    offset: int


def reject_null(value):
    """Za PATCH sheme: neposlano polje je dopušteno, poslani null nije.

    Validator se poziva samo za poslana polja, pa izostavljeno polje ostaje
    None i ne ulazi u model_dump(exclude_unset=True).
    """
    if value is None:
        raise ValueError("Polje ne smije biti null; izostavite ga ako se ne mijenja.")
    return value
