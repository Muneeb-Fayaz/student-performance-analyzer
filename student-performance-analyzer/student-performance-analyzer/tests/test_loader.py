from pathlib import Path

import pytest

from student_analyzer.loader import DataError, load_students


def write_csv(tmp_path, text, encoding="utf-8"):
    path = tmp_path / "data.csv"
    path.write_text(text, encoding=encoding)
    return path


def test_loads_students_and_scores(csv_path):
    students = load_students(csv_path)

    assert [s.name for s in students] == ["Asha", "Ben", "Chen", "Dina"]
    assert students[1].scores == {"Math": 70.0, "Physics": 55.0, "English": 80.0}


def test_blank_cell_is_skipped_not_zero(tmp_path):
    path = write_csv(tmp_path, "name,Math,English\nAsha,90,\n")

    (asha,) = load_students(path)

    assert asha.scores == {"Math": 90.0}


def test_tolerates_excel_bom_and_messy_headers(tmp_path):
    path = write_csv(tmp_path, " Name , Math \nAsha,90\n", encoding="utf-8-sig")

    (asha,) = load_students(path)

    assert asha.name == "Asha"
    assert asha.scores == {"Math": 90.0}


def test_missing_file(tmp_path):
    with pytest.raises(DataError, match="Could not find"):
        load_students(tmp_path / "nope.csv")


def test_empty_file(tmp_path):
    with pytest.raises(DataError, match="empty"):
        load_students(write_csv(tmp_path, ""))


def test_header_without_students(tmp_path):
    with pytest.raises(DataError, match="no students"):
        load_students(write_csv(tmp_path, "name,Math\n"))


def test_needs_a_name_column(tmp_path):
    with pytest.raises(DataError, match="'name' column"):
        load_students(write_csv(tmp_path, "student,Math\nAsha,90\n"))


def test_needs_at_least_one_subject(tmp_path):
    with pytest.raises(DataError, match="subject column"):
        load_students(write_csv(tmp_path, "name\nAsha\n"))


def test_non_numeric_mark_reports_the_line(tmp_path):
    with pytest.raises(DataError, match=r"Line 2.*'abc'.*not a number"):
        load_students(write_csv(tmp_path, "name,Math\nAsha,abc\n"))


@pytest.mark.parametrize("bad", ["101", "-1", "nan", "inf"])
def test_marks_must_be_between_0_and_100(tmp_path, bad):
    with pytest.raises(DataError, match="outside 0-100"):
        load_students(write_csv(tmp_path, f"name,Math\nAsha,{bad}\n"))


def test_duplicate_names_are_rejected(tmp_path):
    with pytest.raises(DataError, match="more than once"):
        load_students(write_csv(tmp_path, "name,Math\nAsha,90\nasha,80\n"))


def test_empty_name_is_rejected(tmp_path):
    with pytest.raises(DataError, match="name is empty"):
        load_students(write_csv(tmp_path, "name,Math\n,90\n"))


def test_the_bundled_sample_file_is_valid():
    sample = Path(__file__).resolve().parent.parent / "data" / "sample_students.csv"

    students = load_students(sample)

    assert len(students) == 12
    assert "Computer Science" in students[0].scores
