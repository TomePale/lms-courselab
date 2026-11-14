from datetime import datetime
from enum import Enum


class CoursePhase(str, Enum):
    ENROLLMENT_OPEN = "enrollment_open"  # now < enrollment_deadline
    ENROLLMENT_CLOSED = "enrollment_closed"  # deadline <= now < start_date
    IN_PROGRESS = "in_progress"  # start_date <= now < end_date
    FINISHED = "finished"  # now >= end_date


def compute_phase(course, now: datetime) -> CoursePhase:
    """Faza se ne sprema nego računa pri svakom zahtjevu, pa nikad ne zaostaje
    za vremenom. course je model Course ili shema CourseRead (oba imaju tri
    datuma). Funkcija ne dira bazu i ne odlučuje što je dopušteno; to radi
    servis. now se prima kao argument, pa je funkciju lako testirati."""
    if now < course.enrollment_deadline:
        return CoursePhase.ENROLLMENT_OPEN
    if now < course.start_date:
        return CoursePhase.ENROLLMENT_CLOSED
    if now < course.end_date:
        return CoursePhase.IN_PROGRESS
    return CoursePhase.FINISHED
