"""Pytest execution backend.

Mirrors ``execute/maven.py``: baseline the original (unmutated) project, then per
mutant restore the source, run the equivalence/compilable checks, splice the
mutant into the source, and run the project's tests to decide survived/killed.

A mutant whose test run raises an error that is **not** a legitimate test failure
(an ``AssertionError`` or pytest ``Failed``) — a runtime crash, import/collection
error, etc. — is not a **competent** mutant: it is reported as not competent rather
than killed. Only a clean test failure counts as a real kill. Python is not
compiled, so this backend's column is COMPETENT (cf. COMPILABLE for Java/Maven).

Named ``pytest_runner`` (not ``pytest``) so it does not shadow the installed
``pytest`` package on import.
"""

import os
import re
import shutil
import subprocess
import sys
from os.path import isfile, join
from pathlib import Path

from checks.compilable import check_mutant_compilable
from checks.syntactic_equivalence import check_mutant_equivalent
from util.io import write_mutant_summary
from util.rewrite_method import rewrite_method


# Exceptions pytest raises for a legitimate test failure (assertion / pytest.fail
# / a `raises` block that did not raise) — these are real kills, not mutant crashes.
_ASSERTION_LIKE = {"AssertionError", "Failed"}


def _has_non_assertion_error(output):
    """True if a pytest traceback reports an exception that is not a legitimate
    test failure — i.e. the mutant crashed rather than being caught by a test."""
    for line in output.splitlines():
        m = re.match(r"E\s+([\w.]+)", line)
        if not m:
            continue
        tok = m.group(1).rsplit(".", 1)[-1]   # e.g. _pytest.outcomes.Failed -> Failed
        if tok in _ASSERTION_LIKE:
            continue
        if tok.endswith("Error") or tok.endswith("Exception"):
            return True
    return False


def _execute(project_root, output_path=None, approach=None, label=None):
    """Run the project's tests with pytest."""
    command = [sys.executable, "-m", "pytest", "-q", str(project_root)]
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, check=False
        )
    except FileNotFoundError as exc:
        raise SystemExit(
            "pytest is not installed for the current interpreter "
            f"({sys.executable}). Install pytest to use the 'pytest' runtool."
        ) from exc

    if output_path is not None and approach and label:
        test_dir = Path(output_path, approach + "-test")
        test_dir.mkdir(parents=True, exist_ok=True)
        safe = str(label).replace(os.sep, "_")
        (test_dir / f"{safe}_test.txt").write_text(
            f"$ {' '.join(command)}\n# exit code: {result.returncode}\n\n"
            f"{result.stdout}"
        )

    passed = result.returncode == 0
    return passed, (not passed and _has_non_assertion_error(result.stdout))


def run_mutants(
    project_root,
    original_file,
    output_path,
    method_start_byte,
    method_end_byte,
    duplicate,
    approach,
    language,
):
    """Execute all mutants using pytest."""
    mutants_dir = Path(output_path, approach + "-mutants")
    mutant_files = [f for f in os.listdir(mutants_dir) if isfile(join(mutants_dir, f))]
    original_method_path = language.original_method_path(output_path)

    mutants = [["MUTANT", "EQUIVALENCE", "COMPETENT", "SURVIVES"]]

    baseline_passed, _ = _execute(project_root, output_path, approach, "ORIGINAL")
    if not baseline_passed:
        raise IOError(
            "The original (unmutated) project did not pass pytest, so mutants "
            "cannot be evaluated against it. Run it manually to see why: "
            f"{sys.executable} -m pytest {project_root}"
        )

    for mutant_file in mutant_files:
        mutant_output = [mutant_file]
        print("Evaluating Mutant: ", mutant_file)
        if duplicate.exists():
            shutil.copy2(duplicate, original_file)

        path = Path(mutants_dir, mutant_file)
        mutant_equivalent = check_mutant_equivalent(path, original_method_path, language)
        mutant_output.append(mutant_equivalent)

        rewrite_method(original_file, method_start_byte, method_end_byte, path)

        mutant_competent = check_mutant_compilable(original_file, language)
        mutant_survives = False
        if mutant_competent:
            passed, non_assertion_error = _execute(
                project_root, output_path, approach, mutant_file
            )
            # A non-assertion error means the mutant crashed the tests rather than
            # being caught by a test — it is not a competent mutant.
            if non_assertion_error:
                mutant_competent = False
            else:
                mutant_survives = passed

        mutant_output.append(mutant_competent)
        mutant_output.append(str(mutant_survives))

        mutants.append(mutant_output)

    write_mutant_summary(mutants_dir, mutants)
