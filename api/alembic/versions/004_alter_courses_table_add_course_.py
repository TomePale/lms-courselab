"""alter_courses_table_add_course_constraints

Revision ID: 004
Revises: 003
Create Date: 2026-11-15 00:00:13.230215

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '004'
down_revision: Union[str, Sequence[str], None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # UNIQUE je autogenerate prepoznao sam
    op.create_unique_constraint(
        op.f("uq_courses_trainer_id_title"), "courses", ["trainer_id", "title"]
    )
    # CHECK je dopisan ručno: autogenerate ne prepoznaje nova CHECK ograničenja
    # na postojećoj tablici. op.f() znači: ime je već konačno, naming
    # convention ga ne smije još jednom obraditi.
    op.create_check_constraint(
        op.f("ck_courses_dates"),
        "courses",
        "enrollment_deadline <= start_date AND start_date < end_date",
    )


def downgrade() -> None:
    # Obrnutim redom od upgrade()
    op.drop_constraint(op.f("ck_courses_dates"), "courses", type_="check")
    op.drop_constraint(op.f("uq_courses_trainer_id_title"), "courses", type_="unique")