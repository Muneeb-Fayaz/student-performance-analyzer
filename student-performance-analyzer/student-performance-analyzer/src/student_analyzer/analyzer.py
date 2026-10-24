"""All the number-crunching lives here. Nothing in this file prints anything,
which keeps it easy to test and easy to reuse from another program."""

from __future__ import annotations

import difflib
from dataclasses import dataclass
from statistics import mean, median, pstdev
from typing import Optional

from .models import Student

PASS_MARK = 60.0

# Highest band first - letter_grade() walks down the list until a cutoff fits.
GRADE_BANDS = (("A", 90.0), ("B", 80.0), ("C", 70.0), ("D", 60.0))
GRADE_ORDER = ("A", "B", "C", "D", "F")


@dataclass
class SubjectStats:
    """Everything we want to know about one subject across the whole class."""

    subject: str
    count: int          # how many students have a mark in this subject
    mean: float
    median: float
    highest: float
    lowest: float
    spread: float       # standard deviation: bigger means marks are more scattered
    top_student: str


def letter_grade(score: float) -> str:
    for letter, cutoff in GRADE_BANDS:
        if score >= cutoff:
            return letter
    return "F"


def class_average(students: list[Student]) -> float:
    """Average of each student's own average. Students with no marks are left out."""
    averages = [s.average for s in students if s.scores]
    return mean(averages) if averages else 0.0


def subject_stats(students: list[Student]) -> dict[str, SubjectStats]:
    """Per-subject statistics, in the same order the subjects appear in the CSV."""
    stats: dict[str, SubjectStats] = {}

    for subject in _subjects_in_order(students):
        # Keep (mark, name) pairs so we can also say who scored highest.
        entries = [(s.scores[subject], s.name) for s in students if subject in s.scores]
        if not entries:
            continue

        values = [mark for mark, _ in entries]
        top_mark, top_name = max(entries, key=lambda entry: entry[0])

        stats[subject] = SubjectStats(
            subject=subject,
            count=len(values),
            mean=mean(values),
            median=median(values),
            highest=top_mark,
            lowest=min(values),
            spread=pstdev(values),
            top_student=top_name,
        )
    return stats


def rank_students(students: list[Student]) -> list[tuple[int, Student]]:
    """Best average first. Students who are level share a rank (1, 1, 3, 4...).

    "Level" means the same average once rounded to one decimal place - the same
    precision we show on screen - so the ranks never contradict what you see.
    """
    ordered = sorted(students, key=lambda s: (-s.average, s.name.lower()))

    ranked: list[tuple[int, Student]] = []
    rank = 0
    previous: Optional[float] = None

    for position, student in enumerate(ordered, start=1):
        current = round(student.average, 1)
        if current != previous:
            rank = position
            previous = current
        ranked.append((rank, student))
    return ranked


def at_risk_students(
    students: list[Student], pass_mark: float = PASS_MARK
) -> list[tuple[Student, list[str]]]:
    """Students with at least one subject below the pass mark, lowest average first.

    Each result is (student, [the subjects they're struggling in]).
    """
    flagged = []
    for student in students:
        failing = [subject for subject, mark in student.scores.items() if mark < pass_mark]
        if failing:
            flagged.append((student, failing))

    flagged.sort(key=lambda item: item[0].average)
    return flagged


def grade_distribution(students: list[Student]) -> dict[str, int]:
    """How many students landed in each letter grade, based on their overall average."""
    counts = {letter: 0 for letter in GRADE_ORDER}
    for student in students:
        if student.scores:
            counts[letter_grade(student.average)] += 1
    return counts


def find_student(students: list[Student], name: str) -> Optional[Student]:
    """Look a student up by name, ignoring capitals and stray spaces."""
    wanted = name.strip().lower()
    for student in students:
        if student.name.lower() == wanted:
            return student
    return None


def suggest_names(students: list[Student], typed: str, limit: int = 3) -> list[str]:
    """For typos: the real names that look most like what the user typed."""
    by_lowercase = {s.name.lower(): s.name for s in students}
    close = difflib.get_close_matches(typed.strip().lower(), list(by_lowercase), n=limit, cutoff=0.6)
    return [by_lowercase[match] for match in close]


def _subjects_in_order(students: list[Student]) -> list[str]:
    # dict.fromkeys removes duplicates while remembering the order we first saw each one.
    return list(dict.fromkeys(subject for s in students for subject in s.scores))
