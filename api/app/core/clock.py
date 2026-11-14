from datetime import datetime, timezone


def now() -> datetime:
    """Trenutno vrijeme u UTC-u. Cijela aplikacija vrijeme čita samo ovdje.

    Jedno mjesto znači da freezegun u testovima pouzdano zamrzne svako
    pravilo koje ovisi o vremenu, a vrijeme uvijek nosi vremensku zonu.
    """
    return datetime.now(timezone.utc)