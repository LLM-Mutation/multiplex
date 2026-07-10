import csv
import subprocess
import types
from pathlib import Path

import pytest

# `execute.defects4j` is imported the runtime way (multiplex/ on sys.path); see
# tests/execute/conftest.py.
from execute import defects4j

METHOD = "int f(int n) { return n; }"


@pytest.fixture(autouse=True)
def _jdk_env(monkeypatch):
    # _execute copies the environment and sets JAVA_HOME = JDK_11; without it the
    # real code KeyErrors before ever calling subprocess.
    monkeypatch.setenv("JDK_11", "/fake/jdk-11")


def _run_returning(stdout):
    """A subprocess.run stub: the defects4j test call yields `stdout`; the rm/pkill
    housekeeping calls get a harmless result."""

    def run(command, *args, **kwargs):
        return types.SimpleNamespace(stdout=stdout, stderr="")

    return run


# --------------------------------------------------------------------------- #
# _execute: maps a Defects4J run to a survives/killed boolean                   #
# --------------------------------------------------------------------------- #


def test_execute_true_when_no_failing_tests(monkeypatch):
    monkeypatch.setattr(
        defects4j.subprocess, "run", _run_returning("Tests: 5\nFailing tests: 0\n")
    )
    assert defects4j._execute("proj") is True


def test_execute_false_when_tests_fail(monkeypatch):
    monkeypatch.setattr(
        defects4j.subprocess,
        "run",
        _run_returning("Failing tests: 2\n  - com.example.FooTest::bar\n"),
    )
    assert defects4j._execute("proj") is False


def test_execute_false_on_timeout(monkeypatch):
    # A slow mutant exceeds the timeout -> TimeoutExpired; the housekeeping pkill
    # runs and the run is reported as killed (False) instead of crashing.
    def run(command, *args, **kwargs):
        if command[0] == "defects4j":
            raise subprocess.TimeoutExpired(cmd="defects4j", timeout=1)
        return types.SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(defects4j.subprocess, "run", run)
    assert defects4j._execute("proj", file="C.java", approach="basic", timer=1) is False


def test_execute_writes_test_output_file_when_timed(tmp_path, monkeypatch):
    # With a timer, _execute persists the run's stderr+stdout to
    # output/{approach}-test/{file without .java}_test.txt, and still classifies
    # from stdout. This is the Defects4J-specific branch (path building via
    # .removesuffix, the mkdir, the stderr+stdout write) that the untimed calls
    # never reach.
    def run(command, *args, **kwargs):
        if command[0] == "defects4j":
            return types.SimpleNamespace(
                stdout="Running tests...\nFailing tests: 0\n", stderr="warn: noisy\n"
            )
        return types.SimpleNamespace(stdout="", stderr="")

    monkeypatch.setattr(defects4j.subprocess, "run", run)

    survives = defects4j._execute(
        str(tmp_path), file="mutant_0.java", approach="basic", timer=5
    )

    assert survives is True
    out_file = tmp_path / "output" / "basic-test" / "mutant_0_test.txt"
    assert out_file.exists()
    # stderr is written before stdout.
    assert out_file.read_text() == "warn: noisy\nRunning tests...\nFailing tests: 0\n"


# --------------------------------------------------------------------------- #
# run_mutants: full evaluation loop over a mutants directory                    #
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
    defects4j.run_mutants(
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

    # Stand in for `defects4j test`: the suite fails (mutant killed) only when the
    # injected source returns n + 1; every other state passes. _execute is called
    # both as _execute(project_root) and _execute(project_root, file, approach,
    # timer=...), so the stub must accept the extra args.
    monkeypatch.setattr(
        defects4j,
        "_execute",
        lambda project_root, *a, **k: "return n + 1" not in Path(src).read_text(),
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
    monkeypatch.setattr(defects4j, "_execute", lambda project_root, *a, **k: False)
    with pytest.raises(IOError):
        _run(project)


def test_run_mutants_skips_tests_for_noncompilable_mutant(project, monkeypatch):
    # Keep only the non-compilable mutant.
    for f in project["mutants"].glob("*.java"):
        f.unlink()
    (project["mutants"] / "mutant_broken.java").write_text("int f(int n) { { return n; }")

    calls = {"n": 0}

    def counting_execute(project_root, *a, **k):
        calls["n"] += 1
        return True

    monkeypatch.setattr(defects4j, "_execute", counting_execute)
    _run(project)

    # Only the baseline runs the suite; the non-compilable mutant is not tested.
    assert calls["n"] == 1
    _, data = _summary(project)
    assert data["mutant_broken.java"][1:] == ["False", "False"]
