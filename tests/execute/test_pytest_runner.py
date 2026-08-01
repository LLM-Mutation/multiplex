import csv
import sys
import types
from pathlib import Path

import pytest

# `execute.pytest_runner` is imported the runtime way (multiplex/ on sys.path);
# see tests/execute/conftest.py.
from execute import pytest_runner
from languages import get_language

PYTHON = get_language("python")

METHOD = "def f(n):\n    return n\n"


# --------------------------------------------------------------------------- #
# _has_non_assertion_error: assertion / Failed are legit; other errors crash   #
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "output, expected",
    [
        ("E   AssertionError: x", False),
        ("E       assert 1 == 2", False),
        ("E   Failed: DID NOT RAISE <class 'ValueError'>", False),
        ("E   _pytest.outcomes.Failed: nope", False),
        ("547 passed", False),
        ("E   TypeError: bad", True),
        ("E       NameError: name 'x' is not defined", True),
        ("E   ImportError: cannot import name 'y'", True),
    ],
)
def test_has_non_assertion_error(output, expected):
    assert pytest_runner._has_non_assertion_error(output) is expected


# --------------------------------------------------------------------------- #
# _execute: returns (passed, non_assertion_error)                              #
# --------------------------------------------------------------------------- #


def _run_returning(returncode, stdout=""):
    def run(command, *args, **kwargs):
        return types.SimpleNamespace(returncode=returncode, stdout=stdout)

    return run


def test_execute_passes_on_zero_exit(monkeypatch):
    monkeypatch.setattr(pytest_runner.subprocess, "run", _run_returning(0))
    assert pytest_runner._execute("proj") == (True, False)


def test_execute_killed_by_assertion(monkeypatch):
    monkeypatch.setattr(
        pytest_runner.subprocess, "run", _run_returning(1, "E   AssertionError: x")
    )
    assert pytest_runner._execute("proj") == (False, False)


def test_execute_flags_non_assertion_crash(monkeypatch):
    monkeypatch.setattr(
        pytest_runner.subprocess, "run", _run_returning(1, "E   TypeError: bad")
    )
    assert pytest_runner._execute("proj") == (False, True)


def test_execute_uses_argv_list_not_shell(monkeypatch):
    captured = {}

    def fake_run(command, *args, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return types.SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(pytest_runner.subprocess, "run", fake_run)

    assert pytest_runner._execute("/path with spaces/proj") == (True, False)
    assert isinstance(captured["command"], list)
    assert captured["command"][:3] == [sys.executable, "-m", "pytest"]
    assert "/path with spaces/proj" in captured["command"]
    assert captured["kwargs"].get("shell", False) is False


def test_execute_reports_missing_pytest_clearly(monkeypatch):
    def raise_fnf(*a, **k):
        raise FileNotFoundError(2, "No such file or directory", sys.executable)

    monkeypatch.setattr(pytest_runner.subprocess, "run", raise_fnf)
    with pytest.raises(SystemExit) as exc:
        pytest_runner._execute("proj")
    assert "pytest" in str(exc.value).lower()


# --------------------------------------------------------------------------- #
# run_mutants: full evaluation loop over a mutants directory                   #
# --------------------------------------------------------------------------- #


@pytest.fixture
def project(tmp_path):
    """A synthetic Python source file + backup, output dir, and four mutants."""
    source = METHOD
    src = tmp_path / "mod.py"
    src.write_text(source)
    (tmp_path / "mod.py.orig").write_text(source)

    output = tmp_path / "output"
    output.mkdir()
    (output / "original_method.py").write_text(METHOD)

    mutants = output / "basic-mutants"
    mutants.mkdir()
    # equivalent: only a comment differs -> AST-equal, competent, survives
    (mutants / "mutant_equivalent.py").write_text("# same behaviour\n" + METHOD)
    # killed: changes behaviour -> competent, tests fail on an assertion
    (mutants / "mutant_killed.py").write_text("def f(n):\n    return n + 1\n")
    # crash: parses, but raises a non-assertion error at run -> not competent
    (mutants / "mutant_crash.py").write_text("def f(n):\n    return oops(n)\n")
    # broken: unterminated call -> does not parse, tests never run
    (mutants / "mutant_broken.py").write_text("def f(n):\n    return foo(n\n")

    return {
        "project_root": str(tmp_path),
        "src": str(src),
        "duplicate": Path(str(src) + ".orig"),
        "output": output,
        "mutants": mutants,
        "start": source.index(METHOD),
        "end": source.index(METHOD) + len(METHOD),
    }


def _run(project, approach="basic"):
    pytest_runner.run_mutants(
        project["project_root"],
        project["src"],
        project["output"],
        project["start"],
        project["end"],
        project["duplicate"],
        approach,
        PYTHON,
    )


def _summary(project):
    with open(Path(project["mutants"], "mutant_summary.csv")) as f:
        rows = list(csv.reader(f))
    return rows[0], {r[0]: r[1:] for r in rows[1:]}


def _fake_execute(src):
    """Stand in for pytest, deciding from the spliced source (mod.py):
    `n + 1` -> assertion kill; `oops` -> non-assertion crash; else passes."""

    def execute(project_root, *a, **k):
        text = Path(src).read_text()
        if "oops" in text:
            return (False, True)     # crashed -> not competent
        if "return n + 1" in text:
            return (False, False)    # assertion kill
        return (True, False)         # passes

    return execute


def test_run_mutants_writes_summary_with_correct_classification(project, monkeypatch):
    monkeypatch.setattr(pytest_runner, "_execute", _fake_execute(project["src"]))

    _run(project)

    header, data = _summary(project)
    assert header == ["MUTANT", "EQUIVALENCE", "COMPETENT", "SURVIVES"]
    assert len(data) == 4
    # [EQUIVALENCE, COMPETENT, SURVIVES]
    assert data["mutant_equivalent.py"] == ["True", "True", "True"]
    assert data["mutant_killed.py"] == ["False", "True", "False"]
    assert data["mutant_crash.py"][1:] == ["False", "False"]   # non-assertion -> not competent
    assert data["mutant_broken.py"][1:] == ["False", "False"]  # unparsable -> not competent


def test_run_mutants_writes_per_mutant_test_logs(project, monkeypatch):
    # Real _execute writes the logs; fake only the pytest subprocess.
    monkeypatch.setattr(
        pytest_runner.subprocess, "run", _run_returning(0, "547 passed")
    )
    _run(project)

    test_dir = project["output"] / "basic-test"
    assert (test_dir / "ORIGINAL_test.txt").is_file()
    assert (test_dir / "mutant_killed.py_test.txt").is_file()  # a competent mutant that ran


def test_run_mutants_raises_when_baseline_fails(project, monkeypatch):
    monkeypatch.setattr(pytest_runner, "_execute", lambda *a, **k: (False, False))
    with pytest.raises(IOError):
        _run(project)


def test_run_mutants_skips_tests_for_noncompetent_mutant(project, monkeypatch):
    # Keep only the unparsable mutant.
    for f in project["mutants"].glob("*.py"):
        f.unlink()
    (project["mutants"] / "mutant_broken.py").write_text("def f(n):\n    return foo(n\n")

    calls = {"n": 0}

    def counting_execute(*a, **k):
        calls["n"] += 1
        return (True, False)

    monkeypatch.setattr(pytest_runner, "_execute", counting_execute)
    _run(project)

    # Only the baseline runs the suite; the unparsable mutant is not tested.
    assert calls["n"] == 1
    _, data = _summary(project)
    assert data["mutant_broken.py"][1:] == ["False", "False"]
