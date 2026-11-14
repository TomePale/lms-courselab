# Uvoz svih modela registrira ih u Base.metadata.
# Alembic autogenerate vidi samo modele koji su ovdje uvezeni.
from app.models.base import Base

__all__ = ["Base"]
