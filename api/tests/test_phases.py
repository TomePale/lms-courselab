from datetime import timedelta

from app.core.phases import CoursePhase, compute_phase
from app.models import Course
from tests.conftest import DEADLINE, END, START

# Jedinični test bez baze i API-ja: funkcija samo uspoređuje vrijeme s datumima
COURSE = Course(enrollment_deadline=DEADLINE, start_date=START, end_date=END)
SECOND = timedelta(seconds=1)


def test_closed_exactly_at_deadline():
    assert compute_phase(COURSE, DEADLINE) == CoursePhase.ENROLLMENT_CLOSED


def test_in_progress_exactly_at_start():
    assert compute_phase(COURSE, START) == CoursePhase.IN_PROGRESS


def test_finished_exactly_at_end():
    assert compute_phase(COURSE, END) == CoursePhase.FINISHED
