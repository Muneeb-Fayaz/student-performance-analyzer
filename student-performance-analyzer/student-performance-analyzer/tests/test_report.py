import csv

from student_analyzer.report import (
    at_risk_report,
    bar,
    format_table,
    ranking_report,
    student_report,
    subjects_report,
    summary_report,
    write_summary_csv,
)


def test_bar_fills_proportionally():
    assert bar(50, 100, 10) == "█████░░░░░"
    assert bar(0, 100, 10) == "░" * 10
    assert bar(100, 100, 10) == "█" * 10


def test_bar_never_overflows_or_goes_negative():
    assert bar(250, 100, 10) == "█" * 10
    assert bar(-20, 100, 10) == "░" * 10


def test_format_table_aligns_columns():
    table = format_table(["Name", "Score"], [("Asha", 90), ("Christopher", 5)], align="<>")

    assert table.splitlines() == [
        "Name         Score",
        "-----------  -----",
        "Asha            90",
        "Christopher      5",
    ]


def test_summary_report_has_the_headline_numbers(students):
    text = summary_report(students)

    assert "Students analysed : 4" in text
    assert "Class average     : 74.6 (C)" in text
    assert "Top performer     : Asha (90.0)" in text
    assert "2 student(s) below 60" in text


def test_ranking_report_shows_tied_ranks(students):
    lines = ranking_report(students).splitlines()
    rows = [line.split() for line in lines[4:]]  # skip title, underline, blank, header... then the rule

    names_in_order = [row[1] for row in rows if len(row) > 1 and row[0].isdigit()]
    assert names_in_order == ["Asha", "Dina", "Ben", "Chen"]
    assert [row[0] for row in rows if row[0].isdigit()] == ["1", "1", "3", "4"]


def test_ranking_report_can_show_only_the_top_n(students):
    text = ranking_report(students, top=2)

    assert "TOP 2 STUDENTS" in text
    assert "Ben" not in text and "Chen" not in text


def test_subjects_report_lists_every_subject(students):
    text = subjects_report(students)

    for subject in ("Math", "Physics", "English"):
        assert subject in text
    assert "Average by subject" in text


def test_student_report_compares_with_the_class(students):
    text = student_report(students[1], students)  # Ben

    assert "REPORT CARD: Ben" in text
    assert "Rank     : 3 of 4" in text
    assert "Weakest  : Physics" in text
    assert "vs class" in text


def test_student_report_handles_a_student_with_no_marks(students):
    ghost = type(students[0])("Ghost")

    text = student_report(ghost, students + [ghost])

    assert "No marks recorded" in text


def test_at_risk_report_names_the_failing_subjects(students):
    text = at_risk_report(students)

    assert "Chen" in text and "Math (50.0), Physics (40.0)" in text
    assert "Asha" not in text


def test_at_risk_report_when_everyone_passes(students):
    assert "Nobody is below the pass mark" in at_risk_report(students, pass_mark=10)


def test_write_summary_csv_round_trip(students, tmp_path):
    out = write_summary_csv(tmp_path / "nested" / "report.csv", students)

    with out.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))

    assert [r["name"] for r in rows] == ["Asha", "Dina", "Ben", "Chen"]
    assert rows[0]["rank"] == "1" and rows[0]["grade"] == "A" and rows[0]["at_risk"] == "no"
    assert rows[3]["at_risk"] == "yes" and rows[3]["weakest_subject"] == "Physics"
