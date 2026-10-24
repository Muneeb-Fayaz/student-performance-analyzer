"""Shared test fixtures: a tiny, hand-checkable class used by most tests.

The numbers are picked so the answers are easy to verify with a calculator:
    Asha  -> 95, 90, 85  (average 90.0)
    Dina  -> exactly the same as Asha, to test ties
    Ben   -> 70, 55, 80  (average 68.3, failing Physics)
    Chen  -> 50, 40, 60  (average 50.0, failing Math and Physics)
"""

import pytest

from student_analyzer.models import Student

SAMPLE_CSV = """name,Math,Physics,English
Asha,95,90,85
Ben,70,55,80
Chen,50,40,60
Dina,95,90,85
"""


@pytest.fixture
def students():
    return [
        Student("Asha", {"Math": 95.0, "Physics": 90.0, "English": 85.0}),
        Student("Ben", {"Math": 70.0, "Physics": 55.0, "English": 80.0}),
        Student("Chen", {"Math": 50.0, "Physics": 40.0, "English": 60.0}),
        Student("Dina", {"Math": 95.0, "Physics": 90.0, "English": 85.0}),
    ]


@pytest.fixture
def csv_path(tmp_path):
    """A real CSV file on disk (pytest cleans it up for us)."""
    path = tmp_path / "students.csv"
    path.write_text(SAMPLE_CSV, encoding="utf-8")
    return path
