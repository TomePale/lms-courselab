# Uvoz svih modela registrira ih u Base.metadata.
# Alembic autogenerate vidi samo modele koji su ovdje uvezeni.
from app.models.base import Base
from app.models.category import Category
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.review import Review
from app.models.user import User  # Primjer modela, zamijeniti stvarnim modelima

__all__ = ["Base", "User", "Course", "Enrollment", "Category", "Review"]
