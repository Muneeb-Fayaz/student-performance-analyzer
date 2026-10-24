from student_analyzer.models import Student


def test_average_best_and_weakest():
    student = Student("Ben", {"Math": 70.0, "Physics": 55.0, "English": 80.0})

    assert student.average == 205 / 3
    assert student.best_subject == "English"
    assert student.weakest_subject == "Physics"


def test_student_with_no_scores_does_not_crash():
    student = Student("Newcomer")

    assert student.average == 0.0
    assert student.best_subject is None
    assert student.weakest_subject is None


def test_tied_subjects_pick_the_first_one():
    student = Student("Tie", {"Math": 80.0, "English": 80.0})

    assert student.best_subject == "Math"
