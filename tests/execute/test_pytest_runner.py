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
# _execute: maps a pytest run to a survives/killed boolean                     #
# --------------------------------------------------------------------------- #


def _run_returning(returncode):
    def run(command, *args, **kwargs):
        return types.SimpleNamespace(returncode=returncode)

    return run


def test_execute_true_on_zero_exit(monkeypatch):
    monkeypatch.setattr(pytest_runner.subprocess, "run", _run_returning(0))
    assert pytest_runner._execute("proj") is True


def test_execute_false_on_nonzero_exit(monkeypatch):
    monkeypatch.setattr(pytest_runner.subprocess, "run", _run_returning(1))
    assert pytest_runner._execute("proj") is False


def test_execute_uses_argv_list_not_shell(monkeypatch):
    captured = {}

    def fake_run(command, *args, **kwargs):
        captured["command"] = command
        captured["kwargs"] = kwargs
        return types.SimpleNamespace(returncode=0)

    monkeypatch.setattr(pytest_runner.subprocess, "run", fake_run)

    assert pytest_runner._execute("/path with spaces/proj") is True
    assert isinstance(captured["command"], list)
    # Runs pytest under multiplex's own interpreter, not a PATH-resolved `python`.
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


def _run_reporting(returncode, stdout):
    def run(command, *args, **kwargs):
        return types.SimpleNamespace(returncode=returncode, stdout=stdout)

    return run


def test_execute_writes_test_output_file_when_labelled(tmp_path, monkeypatch):
    # Given an output path, approach and label, _execute persists the run's
    # captured output to <approach>-test/<label without extension>_test.txt.
    monkeypatch.setattr(
        pytest_runner.subprocess, "run", _run_reporting(1, "1 failed, 2 passed\n")
    )

    assert pytest_runner._execute("proj", tmp_path, "basic", "mutant_killed.py") is False

    # Same naming as the Defects4J runner: the extension is not carried over.
    out_file = tmp_path / "basic-test" / "mutant_killed_test.txt"
    assert out_file.exists()
    body = out_file.read_text()
    assert "1 failed, 2 passed" in body
    assert "# exit code: 1" in body


def test_execute_writes_no_output_file_without_a_label(tmp_path, monkeypatch):
    monkeypatch.setattr(pytest_runner.subprocess, "run", _run_reporting(0, "2 passed\n"))

    assert pytest_runner._execute("proj") is True
    assert list(tmp_path.iterdir()) == []


# --------------------------------------------------------------------------- #
# run_mutants: full evaluation loop over a mutants directory                   #
# --------------------------------------------------------------------------- #


@pytest.fixture
def project(tmp_path):
    """A synthetic Python source file + backup, output dir, and three mutants."""
    source = METHOD
    src = tmp_path / "mod.py"
    src.write_text(source)
    (tmp_path / "mod.py.orig").write_text(source)

    output = tmp_path / "output"
    output.mkdir()
    (output / "original_method.py").write_text(METHOD)

    mutants = output / "basic-mutants"
    mutants.mkdir()
    # equivalent: only a comment differs -> AST-equal, compiles, survives
    (mutants / "mutant_equivalent.py").write_text("# same behaviour\n" + METHOD)
    # killed: changes behaviour -> compiles, tests fail
    (mutants / "mutant_killed.py").write_text("def f(n):\n    return n + 1\n")
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


def test_run_mutants_writes_summary_with_correct_classification(project, monkeypatch):
    src = project["src"]

    # Stand in for `pytest`: the suite fails (mutant killed) only when the
    # injected source returns n + 1; every other state passes.
    monkeypatch.setattr(
        pytest_runner,
        "_execute",
        lambda project_root, *args, **kwargs: "return n + 1" not in Path(src).read_text(),
    )

    _run(project)

    header, data = _summary(project)
    assert header == ["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]
    assert len(data) == 3
    # [EQUIVALENCE, COMPILABLE, SURVIVES]
    assert data["mutant_equivalent.py"] == ["True", "True", "True"]
    assert data["mutant_killed.py"] == ["False", "True", "False"]
    assert data["mutant_broken.py"][1:] == ["False", "False"]  # not compilable, killed


def test_run_mutants_raises_when_baseline_fails(project, monkeypatch):
    monkeypatch.setattr(pytest_runner, "_execute", lambda project_root, *args, **kwargs: False)
    with pytest.raises(IOError):
        _run(project)


def test_run_mutants_skips_tests_for_noncompilable_mutant(project, monkeypatch):
    # Keep only the non-compilable mutant.
    for f in project["mutants"].glob("*.py"):
        f.unlink()
    (project["mutants"] / "mutant_broken.py").write_text("def f(n):\n    return foo(n\n")

    calls = {"n": 0}

    def counting_execute(project_root, *args, **kwargs):
        calls["n"] += 1
        return True

    monkeypatch.setattr(pytest_runner, "_execute", counting_execute)
    _run(project)

    # Only the baseline runs the suite; the non-compilable mutant is not tested.
    assert calls["n"] == 1
    _, data = _summary(project)
    assert data["mutant_broken.py"][1:] == ["False", "False"]
