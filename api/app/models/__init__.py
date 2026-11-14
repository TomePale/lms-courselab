# Uvoz svih modela registrira ih u Base.metadata.
# Alembic autogenerate vidi samo modele koji su ovdje uvezeni.
from app.models.base import Base
from app.models.user import User  # Primjer modela, zamijeniti stvarnim modelima

__all__ = ["Base", "User"]
