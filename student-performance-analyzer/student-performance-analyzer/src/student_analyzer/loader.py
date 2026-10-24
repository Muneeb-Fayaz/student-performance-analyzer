"""Reads student marks from a CSV file and checks that the data makes sense.

Expected layout - one row per student, one column per subject:

    name,Math,Physics,English
    Asha,95,90,85
    Ben,70,,80          <- an empty cell just means "no mark for this subject"
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Union

from .models import Student

MIN_SCORE = 0.0
MAX_SCORE = 100.0


class DataError(Exception):
    """Raised when the CSV is missing, empty, or contains values we can't trust."""


def load_students(path: Union[str, Path]) -> list[Student]:
    """Load every student from the CSV at `path`, or raise DataError with a friendly message."""
    path = Path(path)
    if not path.is_file():
        raise DataError(f"Could not find the data file: {path}")

    try:
        # "utf-8-sig" quietly strips the invisible BOM that Excel likes to add.
        with path.open(newline="", encoding="utf-8-sig") as handle:
            return _read_rows(csv.DictReader(handle))
    except UnicodeDecodeError:
        raise DataError(f"{path} doesn't look like a UTF-8 text file. Try re-saving it as CSV (UTF-8).") from None


def _read_rows(reader: csv.DictReader) -> list[Student]:
    if not reader.fieldnames:
        raise DataError("The file is empty. Expected a header row such as: name,Math,English")

    # Trim stray spaces so " Math " and "Math" count as the same column.
    headers = [h.strip() for h in reader.fieldnames]
    reader.fieldnames = headers

    name_column = next((h for h in headers if h.lower() == "name"), None)
    if name_column is None:
        raise DataError("The CSV needs a 'name' column in its header row.")

    subjects = [h for h in headers if h and h != name_column]
    if not subjects:
        raise DataError("The CSV needs at least one subject column next to 'name'.")

    students: list[Student] = []
    seen_names: set[str] = set()

    for row in reader:
        line = reader.line_num  # the real line in the file, so error messages are easy to act on

        name = (row.get(name_column) or "").strip()
        if not name:
            raise DataError(f"Line {line}: the student's name is empty.")
        if name.lower() in seen_names:
            raise DataError(f"Line {line}: '{name}' appears more than once.")
        seen_names.add(name.lower())

        scores: dict[str, float] = {}
        for subject in subjects:
            raw = (row.get(subject) or "").strip()
            if raw == "":
                continue  # no mark recorded - skip it rather than counting it as zero
            scores[subject] = _parse_score(raw, name, subject, line)

        students.append(Student(name=name, scores=scores))

    if not students:
        raise DataError("The file has a header but no students in it.")
    return students


def _parse_score(raw: str, name: str, subject: str, line: int) -> float:
    try:
        value = float(raw)
    except ValueError:
        raise DataError(f"Line {line}: {name}'s {subject} mark '{raw}' is not a number.") from None

    # Written as "not in range" so that nan (which float() happily accepts) is rejected too.
    if not (MIN_SCORE <= value <= MAX_SCORE):
        raise DataError(
            f"Line {line}: {name}'s {subject} mark {raw} is outside {MIN_SCORE:g}-{MAX_SCORE:g}."
        )
    return value
