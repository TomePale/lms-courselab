from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Category(Base):
    """Kategorija tečaja, npr. "Programiranje". Jedna kategorija ima više tečajeva (1:N)."""

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True uz naming convention daje ograničenje uq_categories_name
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
