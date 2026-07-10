import csv
import subprocess
from pathlib import Path

import pytest

# `execute.maven` is imported the runtime way (multiplex/ on sys.path); see
# tests/execute/conftest.py.
from execute import maven

METHOD = "int f(int n) { return n; }"


# --------------------------------------------------------------------------- #
# _execute: maps a Maven run to a survives/killed boolean                      #
# --------------------------------------------------------------------------- #


def test_execute_true_on_build_success(monkeypatch):
    monkeypatch.setattr(
        maven.subprocess,
        "check_output",
        lambda *a, **k: b"[INFO] Tests run: 3, Failures: 0\n[INFO] BUILD SUCCESS\n",
    )
    assert maven._execute("proj") is True


def test_execute_false_without_build_success(monkeypatch):
    monkeypatch.setattr(
        maven.subprocess,
        "check_output",
        lambda *a, **k: b"[INFO] Tests run: 3, Failures: 1\n[INFO] BUILD FAILURE\n",
    )
    assert maven._execute("proj") is False


def test_execute_false_on_called_process_error(monkeypatch):
    # A killed mutant makes `mvn test` exit non-zero -> CalledProcessError; the
    # captured output is scanned instead of crashing.
    def raise_cpe(*a, **k):
        raise subprocess.CalledProcessError(1, "mvn", output=b"BUILD FAILURE\n")

    monkeypatch.setattr(maven.subprocess, "check_output", raise_cpe)
    assert maven._execute("proj") is False


# --------------------------------------------------------------------------- #
# run_mutants: full evaluation loop over a mutants directory                   #
# --------------------------------------------------------------------------- #


@pytest.fixture
def project(tmp_path):
    """A synthetic source file + backup, output dir, and three mutants."""
    source = "class C {\n    " + METHOD + "\n}\n"
    src = tmp_path / "C.java"
    src.write_text(source)
    (tmp_path / "C.java.orig").write_text(source)

    output = tmp_path / "output"
    output.mkdir()
    (output / "original_method.java").write_text(METHOD)

    mutants = output / "basic-mutants"
    mutants.mkdir()
    # equivalent: only a comment differs -> AST-equal, compiles, survives
    (mutants / "mutant_equivalent.java").write_text("// same behaviour\n" + METHOD)
    # killed: changes behaviour -> compiles, tests fail
    (mutants / "mutant_killed.java").write_text("int f(int n) { return n + 1; }")
    # broken: unbalanced brace -> does not parse, tests never run
    (mutants / "mutant_broken.java").write_text("int f(int n) { { return n; }")

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
    maven.run_mutants(
        project["project_root"],
        project["src"],
        project["output"],
        project["start"],
        project["end"],
        project["duplicate"],
        approach,
    )


def _summary(project):
    with open(Path(project["mutants"], "mutant_summary.csv")) as f:
        rows = list(csv.reader(f))
    return rows[0], {r[0]: r[1:] for r in rows[1:]}


def test_run_mutants_writes_summary_with_correct_classification(project, monkeypatch):
    src = project["src"]

    # Stand in for `mvn clean test`: the build fails (mutant killed) only when
    # the injected source returns n + 1; every other state passes.
    monkeypatch.setattr(
        maven, "_execute", lambda project_root: "return n + 1" not in Path(src).read_text()
    )

    _run(project)

    header, data = _summary(project)
    assert header == ["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]
    assert len(data) == 3
    # [EQUIVALENCE, COMPILABLE, SURVIVES]
    assert data["mutant_equivalent.java"] == ["True", "True", "True"]
    assert data["mutant_killed.java"] == ["False", "True", "False"]
    assert data["mutant_broken.java"][1:] == ["False", "False"]  # not compilable, killed


def test_run_mutants_raises_when_baseline_fails(project, monkeypatch):
    monkeypatch.setattr(maven, "_execute", lambda project_root: False)
    with pytest.raises(IOError):
        _run(project)


def test_run_mutants_skips_tests_for_noncompilable_mutant(project, monkeypatch):
    # Keep only the non-compilable mutant.
    for f in project["mutants"].glob("*.java"):
        f.unlink()
    (project["mutants"] / "mutant_broken.java").write_text("int f(int n) { { return n; }")

    calls = {"n": 0}

    def counting_execute(project_root):
        calls["n"] += 1
        return True

    monkeypatch.setattr(maven, "_execute", counting_execute)
    _run(project)

    # Only the baseline runs the suite; the non-compilable mutant is not tested.
    assert calls["n"] == 1
    _, data = _summary(project)
    assert data["mutant_broken.java"][1:] == ["False", "False"]


def test_run_mutants_restores_source_before_each_mutant(project, monkeypatch):
    # After the run the backup is untouched and the working file has been left
    # holding the last-evaluated mutant (the pipeline's final restore is done by
    # __main__.py, not run_mutants).
    monkeypatch.setattr(maven, "_execute", lambda project_root: True)
    _run(project)
    assert (Path(project["duplicate"]).read_text()).count(METHOD) == 1
