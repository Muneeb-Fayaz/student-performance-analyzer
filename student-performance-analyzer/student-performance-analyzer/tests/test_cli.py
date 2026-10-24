"""End-to-end tests: call main() exactly like the terminal would, then check what was printed."""

import pytest

from student_analyzer.cli import main


def test_summary_command(csv_path, capsys):
    code = main(["summary", "--data", str(csv_path)])

    assert code == 0
    assert "Class average" in capsys.readouterr().out


def test_ranking_command_with_top(csv_path, capsys):
    code = main(["ranking", "-d", str(csv_path), "--top", "1"])

    out = capsys.readouterr().out
    assert code == 0
    assert "Asha" in out and "Ben" not in out


def test_subjects_command(csv_path, capsys):
    assert main(["subjects", "-d", str(csv_path)]) == 0
    assert "SUBJECT BREAKDOWN" in capsys.readouterr().out


def test_student_command_accepts_names_without_quotes(csv_path, capsys):
    assert main(["student", "-d", str(csv_path), "ben"]) == 0
    assert "REPORT CARD: Ben" in capsys.readouterr().out


def test_unknown_student_suggests_a_fix(csv_path, capsys):
    code = main(["student", "-d", str(csv_path), "Benn"])

    err = capsys.readouterr().err
    assert code == 1
    assert "No student called 'Benn'" in err
    assert "Did you mean: Ben" in err


def test_at_risk_command_with_threshold(csv_path, capsys):
    assert main(["at-risk", "-d", str(csv_path), "--threshold", "45"]) == 0
    out = capsys.readouterr().out
    assert "Chen" in out and "Ben" not in out


def test_export_command_writes_a_file(csv_path, tmp_path, capsys):
    target = tmp_path / "out.csv"

    code = main(["export", "-d", str(csv_path), "-o", str(target)])

    assert code == 0
    assert target.exists()
    assert "Saved a summary of 4 students" in capsys.readouterr().out


def test_missing_data_file_gives_a_clean_error(tmp_path, capsys):
    code = main(["summary", "-d", str(tmp_path / "missing.csv")])

    captured = capsys.readouterr()
    assert code == 1
    assert "Error: Could not find the data file" in captured.err
    assert captured.out == ""


def test_bad_arguments_are_rejected_by_argparse(csv_path):
    with pytest.raises(SystemExit) as exit_info:
        main(["ranking", "-d", str(csv_path), "--top", "0"])
    assert exit_info.value.code == 2


def test_a_command_is_required():
    with pytest.raises(SystemExit):
        main([])
