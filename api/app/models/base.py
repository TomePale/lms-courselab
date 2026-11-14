from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

# Pravila imenovanja ograničenja i indeksa. Bez njih PostgreSQL sam bira imena
# (npr. users_email_key), a Alembic ih u downgrade() ne zna pogoditi.
# Ovo osigurava da imena ograničenja i indeksa budu predvidljiva i konzistentna.
# Dokumentacija o SQLAlchemy za više informacija:
# https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

# Bazna klasa za sve modele. Svi modeli trebaju naslijediti ovu klasu.
# Sadrži metapodatke s pravilima imenovanja ograničenja i indeksa.
# Metapodaci se koriste za generiranje SQL naredbi s pravilnim imenima
# ograničenja i indeksa.
# Svi modeli trebaju koristiti ovu baznu klasu kako bi se osigurala
# konzistentna pravila imenovanja.


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)
