# Build Guide: Student Performance Analyzer, step by step

This walks through building the project from an empty folder to a finished GitHub repo.
Each step says what to do, why, and how to check it worked. Budget roughly 2 to 3 hours the first time.

**You need:** Python 3.9+ (`python3 --version`), Git (`git --version`), a free GitHub account, and any code editor.

---

## Step 1. Create the project and a virtual environment

```bash
mkdir student-performance-analyzer && cd student-performance-analyzer
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
git init
```

A virtual environment keeps this project's packages separate from everything else on your machine.
You should see `(.venv)` at the start of your terminal prompt.

## Step 2. Create the folders

```bash
mkdir -p src/student_analyzer tests data docs .github/workflows
touch src/student_analyzer/__init__.py
```

Putting code under `src/` stops Python from accidentally importing your working folder instead of the installed package. It is the layout most professional projects use.

## Step 3. Add sample data

Create `data/sample_students.csv` (copy it from this repo). Real-looking data makes your README screenshots convincing, so include a blank cell and a subject with a space in its name, as the sample does. They are great test cases.

## Step 4. Build the layers, one file at a time

Build from the bottom up. Each file only depends on the ones before it.

| Order | File | Job | Check it with |
|---|---|---|---|
| 1 | `models.py` | The `Student` dataclass with `average`, `best_subject`, `weakest_subject` | `tests/test_models.py` |
| 2 | `loader.py` | Read the CSV, validate every value, raise `DataError` with the line number | `tests/test_loader.py` |
| 3 | `analyzer.py` | Pure maths: grades, subject stats, ranking with ties, at-risk | `tests/test_analyzer.py` |
| 4 | `report.py` | Format results as text: bars, tables, CSV export | `tests/test_report.py` |
| 5 | `cli.py` + `__main__.py` | `argparse` commands that glue it all together | `tests/test_cli.py` |

**The key habit:** after finishing each file, write its tests and run `pytest` before moving on. A bug found one file later is far cheaper than one found five files later.

Ideas worth understanding as you write each layer:

- **models.py**: `@dataclass` generates `__init__` and `__repr__` for you. `@property` lets `student.average` look like a field but compute on demand.
- **loader.py**: never trust input. Every failure raises one custom exception, so the CLI can catch it in one place and print a friendly message instead of a traceback.
- **analyzer.py**: no `print()` calls anywhere. Functions take data and return data.
- **report.py**: functions return strings. The CLI chooses to print them, and tests can check them.
- **cli.py**: `main()` returns an exit code (0 = success, 1 = error) rather than calling `sys.exit()`, which is what makes it testable.

## Step 5. Configure the project

Create `pyproject.toml` (copy from this repo). The two parts worth understanding:

- `[project.scripts]` creates the `student-analyzer` command when someone runs `pip install`.
- `[tool.pytest.ini_options] pythonpath = ["src"]` lets `pytest` find your code without installing.

## Step 6. Run it

```bash
pip install -e ".[dev]"            # editable install: code changes take effect immediately

student-analyzer summary
student-analyzer ranking --top 5
student-analyzer subjects
student-analyzer student Meera Nair
student-analyzer at-risk --threshold 65
student-analyzer export -o report.csv
```

Or without installing:

```bash
PYTHONPATH=src python3 -m student_analyzer summary
```

## Step 7. Test it

```bash
pytest -v                          # run everything, show each test name
pytest tests/test_loader.py        # just one file
pytest -k "tie"                    # only tests with "tie" in their name
pytest -x                          # stop at the first failure
```

You should see `61 passed`. Now try **breaking something on purpose**: change `>= cutoff` to `> cutoff` in `letter_grade` and watch the boundary tests fail. Seeing a test catch a bug is how you learn to trust them.

Optional: measure coverage.

```bash
pip install pytest-cov
pytest --cov=student_analyzer --cov-report=term-missing
```

## Step 8. Add the extras that make a repo look professional

- `README.md`: what it is, features, quick start, real example output, project structure, how to run tests.
- `LICENSE`: MIT is the common choice for portfolio projects. Put your name in it.
- `.gitignore`: keeps `__pycache__`, `.venv` and other clutter out of Git.
- `.github/workflows/tests.yml`: GitHub runs your tests on every push and shows a green badge.

## Step 9. Put it on GitHub

1. On github.com click **New repository**. Name it `student-performance-analyzer`. Leave "Add a README" **unchecked** (you already have one).
2. In your terminal:

```bash
git add .
git status                          # check .venv is NOT listed
git commit -m "Initial commit: Student Performance Analyzer"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/student-performance-analyzer.git
git push -u origin main
```

3. Search the README and LICENSE for `YOUR-USERNAME` / `YOUR NAME` and replace them, then commit again.
4. Open the **Actions** tab and confirm the tests run green.
5. On the repo page, click the gear next to **About**, add a one-line description and topics such as `python`, `cli`, `pytest`, `data-analysis`, `education`.

## Step 10. Polish with small, meaningful commits

Recruiters read your commit history. Instead of one giant commit, build features in a branch and commit as you go:

```bash
git checkout -b feature/weighted-subjects
# ...make changes, add tests...
git commit -am "Add optional subject weights to average calculation"
```

Good next features, roughly in order of how impressive they look:

1. **Weighted subjects** via a `--weights Math=2,English=1` option
2. **Compare two terms** (`compare term1.csv term2.csv`) showing who improved
3. **JSON output** with `--format json`
4. **Matplotlib charts** saved as PNG, with a screenshot in the README
5. **Test coverage badge** using Codecov

## Troubleshooting

| Problem | Fix |
|---|---|
| `ModuleNotFoundError: student_analyzer` | Run `pip install -e ".[dev]"`, or prefix with `PYTHONPATH=src` |
| `student-analyzer: command not found` | Activate the venv: `source .venv/bin/activate` |
| `Could not find the data file` | Run from the project root, or pass `--data path/to/file.csv` |
| Bars show as `?` or garbled boxes on Windows | Use Windows Terminal, or run `chcp 65001` first |
| `pytest: command not found` | `pip install -e ".[dev]"` inside the activated venv |

## Interview talking points

- *"Why is calculation separate from printing?"* Testability and reuse: the same logic could power a web app.
- *"How do you handle bad input?"* One custom exception, validated at the boundary, with line numbers in the messages.
- *"How do ties in rankings work?"* Competition ranking (1, 1, 3), based on the rounded value the user actually sees.
- *"Why no dependencies?"* Zero install friction and nothing to keep patched. I would add Matplotlib only for an optional charts feature.
