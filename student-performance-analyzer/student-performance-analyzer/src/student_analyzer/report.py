"""Turns the numbers from analyzer.py into text you can read in a terminal.

Every function here *returns* a string instead of printing it. That way the
CLI decides where the text goes, and the tests can check it directly.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional, Sequence, Union

from .analyzer import (
    PASS_MARK,
    at_risk_students,
    class_average,
    grade_distribution,
    letter_grade,
    rank_students,
    subject_stats,
)
from .models import Student

BAR_FULL = "█"
BAR_EMPTY = "░"


# ---------------------------------------------------------------- small helpers

def bar(value: float, maximum: float = 100.0, width: int = 30) -> str:
    """A text progress bar, e.g. bar(50, 100, 10) -> '█████░░░░░'."""
    if maximum <= 0:
        return BAR_EMPTY * width
    share = max(0.0, min(value, maximum)) / maximum
    filled = round(width * share)
    return BAR_FULL * filled + BAR_EMPTY * (width - filled)


def format_table(headers: Sequence[str], rows: Sequence[Sequence[object]], align: str = "") -> str:
    """Line columns up neatly. `align` has one character per column: '<' left, '>' right."""
    cells = [[str(cell) for cell in row] for row in rows]
    align = align or "<" * len(headers)

    # Each column is as wide as its longest entry (header included).
    widths = [len(h) for h in headers]
    for row in cells:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], len(cell))

    def one_line(values: Sequence[str]) -> str:
        parts = [f"{value:{a}{w}}" for value, a, w in zip(values, align, widths)]
        return "  ".join(parts).rstrip()

    rule = "  ".join("-" * w for w in widths)
    return "\n".join([one_line(headers), rule] + [one_line(row) for row in cells])


def _title(text: str) -> str:
    return f"{text}\n{'=' * len(text)}"


def _num(value: float) -> str:
    return f"{value:.1f}"


# --------------------------------------------------------------------- reports

def summary_report(students: list[Student], pass_mark: float = PASS_MARK) -> str:
    stats = subject_stats(students)
    overall = class_average(students)
    ranked = rank_students(students)
    at_risk = at_risk_students(students, pass_mark)
    counts = grade_distribution(students)

    top_rank, top_student = ranked[0]
    biggest = max(counts.values()) or 1  # "or 1" avoids dividing by zero for an all-empty class

    lines = [
        _title("STUDENT PERFORMANCE SUMMARY"),
        "",
        f"Students analysed : {len(students)}",
        f"Subjects          : {', '.join(stats)}",
        f"Class average     : {_num(overall)} ({letter_grade(overall)})",
        f"Top performer     : {top_student.name} ({_num(top_student.average)})",
        f"Needs support     : {len(at_risk)} student(s) below {pass_mark:g} in at least one subject",
        "",
        "Grade distribution",
        "------------------",
    ]
    for letter, count in counts.items():
        lines.append(f"  {letter}  {bar(count, biggest, 20)}  {count}")

    return "\n".join(lines)


def ranking_report(students: list[Student], top: Optional[int] = None) -> str:
    ranked = rank_students(students)
    if top is not None:
        ranked = ranked[:top]

    rows = [
        (rank, s.name, _num(s.average), letter_grade(s.average), s.best_subject or "-", s.weakest_subject or "-")
        for rank, s in ranked
    ]
    heading = "CLASS RANKING" if top is None else f"TOP {len(ranked)} STUDENTS"
    table = format_table(
        ["Rank", "Name", "Average", "Grade", "Best subject", "Weakest subject"],
        rows,
        align="><><<<",  # rank and average are numbers, so they line up on the right
    )
    return f"{_title(heading)}\n\n{table}"


def subjects_report(students: list[Student]) -> str:
    stats = subject_stats(students)

    rows = [
        (s.subject, _num(s.mean), _num(s.median), _num(s.highest), _num(s.lowest), _num(s.spread), s.top_student)
        for s in stats.values()
    ]
    table = format_table(
        ["Subject", "Mean", "Median", "High", "Low", "Std dev", "Top student"],
        rows,
        align="<>>>>><",
    )

    label_width = max(len(name) for name in stats)
    chart = [f"{s.subject:<{label_width}}  {bar(s.mean)}  {_num(s.mean)}" for s in stats.values()]

    return "\n".join([_title("SUBJECT BREAKDOWN"), "", table, "", "Average by subject", "------------------", *chart])


def student_report(student: Student, everyone: list[Student]) -> str:
    stats = subject_stats(everyone)
    rank = next(r for r, s in rank_students(everyone) if s is student)

    lines = [
        _title(f"REPORT CARD: {student.name}"),
        "",
        f"Rank     : {rank} of {len(everyone)}",
        f"Average  : {_num(student.average)} ({letter_grade(student.average)})",
        "",
    ]

    if not student.scores:
        lines.append("No marks recorded for this student yet.")
        return "\n".join(lines)

    label_width = max(len(subject) for subject in student.scores)
    for subject, mark in student.scores.items():
        # Compare against the class so a 70 in a hard subject reads differently to a 70 in an easy one.
        gap = mark - stats[subject].mean
        lines.append(
            f"{subject:<{label_width}}  {bar(mark, width=24)}  {_num(mark):>5} "
            f"({letter_grade(mark)})  {gap:+.1f} vs class"
        )

    lines += [
        "",
        f"Strongest: {student.best_subject}",
        f"Weakest  : {student.weakest_subject}",
    ]
    return "\n".join(lines)


def at_risk_report(students: list[Student], pass_mark: float = PASS_MARK) -> str:
    flagged = at_risk_students(students, pass_mark)
    heading = _title(f"AT-RISK STUDENTS (pass mark {pass_mark:g})")

    if not flagged:
        return f"{heading}\n\nNobody is below the pass mark. Nice work, everyone!"

    rows = [
        (
            student.name,
            _num(student.average),
            ", ".join(f"{subject} ({_num(student.scores[subject])})" for subject in failing),
        )
        for student, failing in flagged
    ]
    table = format_table(["Name", "Average", "Below the pass mark in"], rows, align="<><")
    return f"{heading}\n\n{table}"


# ---------------------------------------------------------------------- export

def write_summary_csv(
    path: Union[str, Path], students: list[Student], pass_mark: float = PASS_MARK
) -> Path:
    """Save one row per student (rank, average, grade...) so it can be opened in Excel."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    at_risk_names = {s.name for s, _ in at_risk_students(students, pass_mark)}

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["rank", "name", "average", "grade", "best_subject", "weakest_subject", "at_risk"])
        for rank, student in rank_students(students):
            writer.writerow([
                rank,
                student.name,
                _num(student.average),
                letter_grade(student.average),
                student.best_subject or "",
                student.weakest_subject or "",
                "yes" if student.name in at_risk_names else "no",
            ])
    return path
