import pytest

from student_analyzer.analyzer import (
    at_risk_students,
    class_average,
    find_student,
    grade_distribution,
    letter_grade,
    rank_students,
    subject_stats,
    suggest_names,
)
from student_analyzer.models import Student


@pytest.mark.parametrize(
    "score, expected",
    [(100, "A"), (90, "A"), (89.9, "B"), (80, "B"), (70, "C"), (60, "D"), (59.9, "F"), (0, "F")],
)
def test_letter_grade_boundaries(score, expected):
    assert letter_grade(score) == expected


def test_class_average(students):
    # (90 + 68.33 + 50 + 90) / 4
    assert class_average(students) == pytest.approx(74.5833, abs=0.001)


def test_class_average_ignores_students_without_marks(students):
    students.append(Student("Ghost"))

    assert class_average(students) == pytest.approx(74.5833, abs=0.001)


def test_class_average_of_nobody_is_zero():
    assert class_average([]) == 0.0


def test_subject_stats_for_math(students):
    math = subject_stats(students)["Math"]

    assert math.count == 4
    assert math.mean == 77.5
    assert math.median == 82.5
    assert math.highest == 95.0
    assert math.lowest == 50.0
    assert math.spread == pytest.approx(356.25 ** 0.5)
    assert math.top_student == "Asha"  # Asha and Dina tie; the earlier row wins


def test_subject_stats_keep_csv_column_order(students):
    assert list(subject_stats(students)) == ["Math", "Physics", "English"]


def test_subject_stats_skip_missing_marks():
    class_ = [Student("A", {"Math": 80.0}), Student("B", {"Math": 60.0, "Art": 90.0})]

    stats = subject_stats(class_)

    assert stats["Art"].count == 1
    assert stats["Math"].mean == 70.0


def test_ranking_shares_a_rank_when_tied(students):
    ranked = rank_students(students)

    assert [rank for rank, _ in ranked] == [1, 1, 3, 4]
    assert [s.name for _, s in ranked] == ["Asha", "Dina", "Ben", "Chen"]


def test_at_risk_lists_failing_subjects_lowest_average_first(students):
    flagged = at_risk_students(students)

    assert [(s.name, failing) for s, failing in flagged] == [
        ("Chen", ["Math", "Physics"]),
        ("Ben", ["Physics"]),
    ]


def test_at_risk_respects_a_custom_pass_mark(students):
    flagged = at_risk_students(students, pass_mark=45.0)

    assert [s.name for s, _ in flagged] == ["Chen"]  # only Chen's Physics 40 is below 45


def test_grade_distribution(students):
    assert grade_distribution(students) == {"A": 2, "B": 0, "C": 0, "D": 1, "F": 1}


def test_find_student_ignores_case_and_spaces(students):
    assert find_student(students, "  aSHa ").name == "Asha"
    assert find_student(students, "Nobody") is None


def test_suggest_names_catches_typos(students):
    assert suggest_names(students, "Ashaa") == ["Asha"]
    assert suggest_names(students, "zzzzz") == []
