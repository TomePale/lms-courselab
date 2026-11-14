from datetime import datetime, timedelta, timezone

from app.core.phases import CoursePhase, compute_phase
from app.models import Course
from tests.conftest import DEADLINE, END, START

# Jedinični test bez baze i API-ja: funkcija samo uspoređuje vrijeme s datumima
COURSE = Course(enrollment_deadline=DEADLINE, start_date=START, end_date=END)
SECOND = timedelta(seconds=1)


def test_open_just_before_deadline():
    assert compute_phase(COURSE, DEADLINE - SECOND) == CoursePhase.ENROLLMENT_OPEN


def test_closed_exactly_at_deadline():
    assert compute_phase(COURSE, DEADLINE) == CoursePhase.ENROLLMENT_CLOSED


def test_closed_just_before_start():
    assert compute_phase(COURSE, START - SECOND) == CoursePhase.ENROLLMENT_CLOSED


def test_in_progress_exactly_at_start():
    assert compute_phase(COURSE, START) == CoursePhase.IN_PROGRESS


def test_in_progress_just_before_end():
    assert compute_phase(COURSE, END - SECOND) == CoursePhase.IN_PROGRESS


def test_finished_exactly_at_end():
    assert compute_phase(COURSE, END) == CoursePhase.FINISHED


def test_comparison_is_by_instant_not_by_local_clock():
    # 00:30 po srednjoeuropskom vremenu (UTC+1) je 23:30 UTC prethodnog dana:
    # to je pola sata prije roka, iako lokalni sat već pokazuje 1. ožujka
    cet = timezone(timedelta(hours=1))
    now = datetime(2030, 3, 1, 0, 30, tzinfo=cet)
    assert compute_phase(COURSE, now) == CoursePhase.ENROLLMENT_OPEN
