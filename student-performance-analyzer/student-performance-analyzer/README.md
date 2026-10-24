# Student Performance Analyzer

[![Tests](https://github.com/YOUR-USERNAME/student-performance-analyzer/actions/workflows/tests.yml/badge.svg)](https://github.com/YOUR-USERNAME/student-performance-analyzer/actions/workflows/tests.yml)
![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Dependencies](https://img.shields.io/badge/dependencies-none-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

A command-line tool that reads student marks from a CSV file and turns them into
clear, readable reports: class summaries, rankings, per-subject statistics,
individual report cards, and an early-warning list of students who need support.

It uses **only the Python standard library**, so there is nothing to install beyond Python itself.

## Why I built it

Teachers often have marks sitting in a spreadsheet and want quick answers:
*Who is struggling? Which subject is the hardest? How does one student compare with the class?*
This tool answers those questions in one command, and it is built the way I'd build
something I expected others to maintain: small modules, validated input, friendly errors, and tests.

## Features

- **Summary** of the whole class with a grade distribution chart
- **Ranking** with proper tie handling (1, 1, 3, 4) and an optional `--top N`
- **Subject breakdown**: mean, median, highest, lowest, standard deviation, top scorer
- **Report card** for one student, compared against the class average per subject
- **At-risk list** with a configurable pass mark
- **CSV export** of the ranking to open in Excel
- **Careful input checking**: missing files, bad numbers, out-of-range marks, duplicate names, and Excel's hidden BOM are all handled with messages that point to the exact line
- **Typo help**: `student Meera Nar` suggests *"Did you mean: Meera Nair?"*

## Quick start

```bash
git clone https://github.com/YOUR-USERNAME/student-performance-analyzer.git
cd student-performance-analyzer

# Run it straight from the source folder (no install needed)
PYTHONPATH=src python3 -m student_analyzer summary
```

Or install it so the `student-analyzer` command works anywhere:

```bash
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -e ".[dev]"

student-analyzer summary
```

## Usage

```text
student-analyzer <command> [options]

  summary     class overview and grade distribution
  ranking     rank students by average          (-n/--top N)
  subjects    statistics for each subject
  student     report card for one student       (student Meera Nair)
  at-risk     students below the pass mark      (-t/--threshold 60)
  export      save a ranking summary as CSV     (-o/--output report.csv)

Every command accepts  -d/--data path/to/marks.csv
(default: data/sample_students.csv)
```

### Example output

```text
$ student-analyzer summary
STUDENT PERFORMANCE SUMMARY
===========================

Students analysed : 12
Subjects          : Math, Physics, Chemistry, English, Computer Science
Class average     : 75.5 (C)
Top performer     : Meera Nair (94.8)
Needs support     : 4 student(s) below 60 in at least one subject

Grade distribution
------------------
  A  ████████████████████  3
  B  ████████████████████  3
  C  █████████████░░░░░░░  2
  D  █████████████░░░░░░░  2
  F  █████████████░░░░░░░  2
```

```text
$ student-analyzer ranking --top 5
TOP 5 STUDENTS
==============

Rank  Name          Average  Grade  Best subject      Weakest subject
----  ------------  -------  -----  ----------------  ----------------
   1  Meera Nair       94.8  A      Computer Science  English
   2  Neha Gupta       90.4  A      English           Physics
   3  Aarav Sharma     90.2  A      Computer Science  English
   4  Isha Verma       88.2  B      Physics           English
   5  Sana Khan        82.2  B      English           Computer Science
```

```text
$ student-analyzer subjects
SUBJECT BREAKDOWN
=================

Subject           Mean  Median  High   Low  Std dev  Top student
----------------  ----  ------  ----  ----  -------  -----------
Math              73.0    75.5  97.0  38.0     18.4  Meera Nair
Physics           73.3    76.5  94.0  45.0     15.7  Isha Verma
Chemistry         73.7    75.0  95.0  48.0     16.4  Meera Nair
English           78.8    80.5  94.0  58.0     11.3  Neha Gupta
Computer Science  78.8    78.5  99.0  58.0     13.0  Meera Nair

Average by subject
------------------
Math              ██████████████████████░░░░░░░░  73.0
Physics           ██████████████████████░░░░░░░░  73.3
Chemistry         ██████████████████████░░░░░░░░  73.7
English           ████████████████████████░░░░░░  78.8
Computer Science  ████████████████████████░░░░░░  78.8
```

```text
$ student-analyzer student Meera Nair
REPORT CARD: Meera Nair
=======================

Rank     : 1 of 12
Average  : 94.8 (A)

Math              ███████████████████████░   97.0 (A)  +24.0 vs class
Physics           ██████████████████████░░   93.0 (A)  +19.7 vs class
Chemistry         ███████████████████████░   95.0 (A)  +21.3 vs class
English           ██████████████████████░░   90.0 (A)  +11.2 vs class
Computer Science  ████████████████████████   99.0 (A)  +20.2 vs class

Strongest: Computer Science
Weakest  : English
```

```text
$ student-analyzer at-risk
AT-RISK STUDENTS (pass mark 60)
===============================

Name          Average  Below the pass mark in
------------  -------  ----------------------------------------------------------------------
Tanvi Desai      50.4  Math (38.0), Physics (45.0), Chemistry (50.0), English (58.0)
Kabir Singh      53.8  Math (45.0), Physics (52.0), Chemistry (48.0), Computer Science (58.0)
Vikram Joshi     61.2  Math (56.0), Chemistry (59.0)
Rohan Mehta      65.0  Physics (58.0)
```

## Using your own data

Create a CSV with a `name` column and one column per subject. Empty cells mean
"no mark" and are skipped (they are not counted as zero).

```csv
name,Math,Physics,English
Asha,95,90,85
Ben,70,,80
```

```bash
student-analyzer summary --data my_class.csv
```

Marks must be numbers between 0 and 100. If something is wrong you get a message like:

```text
Error: Line 4: Ben's Math mark 'abc' is not a number.
```

## Project structure

```text
student-performance-analyzer/
├── src/student_analyzer/
│   ├── models.py      # Student dataclass (average, best/weakest subject)
│   ├── loader.py      # CSV reading + validation, raises DataError
│   ├── analyzer.py    # Pure calculations: grades, stats, ranking, at-risk
│   ├── report.py      # Turns results into text (bars, tables, CSV export)
│   ├── cli.py         # argparse commands and exit codes
│   └── __main__.py    # enables `python -m student_analyzer`
├── tests/             # pytest suite (unit + end-to-end CLI tests)
├── data/sample_students.csv
├── docs/BUILD_GUIDE.md
└── pyproject.toml
```

### Design decisions

- **Calculation and display are separate.** `analyzer.py` never prints and `report.py` never calculates. That makes both easy to test and lets the logic be reused in a web app or notebook later.
- **Report functions return strings.** The CLI decides where output goes, so tests assert on the text directly.
- **`main()` returns an exit code** instead of calling `sys.exit()`, so the CLI is testable without spawning subprocesses.
- **Ties share a rank** based on the average rounded to the one decimal place shown on screen, so the ranking never contradicts what the user can see.
- **Zero dependencies** keeps installation trivial and the project easy to review.

## Running the tests

```bash
pip install -e ".[dev]"
pytest -v
```

The suite has 61 tests covering the models, CSV validation, statistics, ranking ties,
report formatting, and every CLI command including error paths. GitHub Actions runs it
on Python 3.9 through 3.13 for every push.

## Roadmap

- [ ] Weighted subjects (e.g. Math counts double)
- [ ] Compare two terms to show who improved
- [ ] Optional Matplotlib charts
- [ ] JSON output for use in other tools

## License

MIT. See [LICENSE](LICENSE).
