"""The command-line front door: figures out what the user asked for and prints the answer."""

from __future__ import annotations

import argparse
import sys
from typing import Optional, Sequence

from . import __version__
from .analyzer import PASS_MARK, find_student, suggest_names
from .loader import DataError, load_students
from .models import Student
from .report import (
    at_risk_report,
    ranking_report,
    student_report,
    subjects_report,
    summary_report,
    write_summary_csv,
)

DEFAULT_DATA = "data/sample_students.csv"


class CommandError(Exception):
    """The user asked for something we can't do (like a student who doesn't exist)."""


def _positive_int(text: str) -> int:
    try:
        value = int(text)
    except ValueError:
        raise argparse.ArgumentTypeError(f"'{text}' is not a whole number") from None
    if value < 1:
        raise argparse.ArgumentTypeError("must be 1 or more")
    return value


def build_parser() -> argparse.ArgumentParser:
    # Options shared by every command live in one parent parser so we only write them once.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "-d", "--data", default=DEFAULT_DATA, metavar="CSV",
        help=f"path to the marks file (default: {DEFAULT_DATA})",
    )

    parser = argparse.ArgumentParser(
        prog="student-analyzer",
        description="Analyse student marks from a CSV file, right in your terminal.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    commands = parser.add_subparsers(dest="command", required=True, metavar="command")

    commands.add_parser("summary", parents=[common], help="class overview and grade distribution")

    ranking = commands.add_parser("ranking", parents=[common], help="rank students by average")
    ranking.add_argument("-n", "--top", type=_positive_int, help="only show the top N students")

    commands.add_parser("subjects", parents=[common], help="statistics for each subject")

    student = commands.add_parser("student", parents=[common], help="report card for one student")
    student.add_argument("name", nargs="+", help="the student's name (quotes optional)")

    risk = commands.add_parser("at-risk", parents=[common], help="students below the pass mark")
    risk.add_argument(
        "-t", "--threshold", type=float, default=PASS_MARK,
        help=f"pass mark to check against (default: {PASS_MARK:g})",
    )

    export = commands.add_parser("export", parents=[common], help="save a ranking summary as CSV")
    export.add_argument("-o", "--output", default="report.csv", help="where to save it (default: report.csv)")

    return parser


def _run_command(args: argparse.Namespace, students: list[Student]) -> str:
    """Turn the chosen command into the text we should print."""
    if args.command == "summary":
        return summary_report(students)

    if args.command == "ranking":
        return ranking_report(students, top=args.top)

    if args.command == "subjects":
        return subjects_report(students)

    if args.command == "at-risk":
        return at_risk_report(students, pass_mark=args.threshold)

    if args.command == "student":
        wanted = " ".join(args.name)
        student = find_student(students, wanted)
        if student is None:
            message = f"No student called '{wanted}' was found."
            suggestions = suggest_names(students, wanted)
            if suggestions:
                message += f" Did you mean: {', '.join(suggestions)}?"
            raise CommandError(message)
        return student_report(student, students)

    if args.command == "export":
        saved = write_summary_csv(args.output, students)
        return f"Saved a summary of {len(students)} students to {saved}"

    raise CommandError(f"Unknown command: {args.command}")  # argparse should stop this first


def main(argv: Optional[Sequence[str]] = None) -> int:
    """Run the tool and return an exit code (0 = success), which makes it easy to test."""
    args = build_parser().parse_args(argv)

    try:
        students = load_students(args.data)
        output = _run_command(args, students)
    except (DataError, CommandError) as problem:
        print(f"Error: {problem}", file=sys.stderr)
        return 1

    print(output)
    return 0


def run() -> None:
    """Entry point for the `student-analyzer` command and `python -m student_analyzer`."""
    # The bar charts use block characters; make sure Windows consoles can print them.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError, OSError):
            pass
    sys.exit(main())
