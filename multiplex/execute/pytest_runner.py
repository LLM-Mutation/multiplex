"""Pytest execution backend.

Mirrors ``execute/maven.py``: baseline the original (unmutated) project, then per
mutant restore the source, run the equivalence/compilable checks, splice the
mutant into the source, and run the project's tests to decide survived/killed.

Named ``pytest_runner`` (not ``pytest``) so it does not shadow the installed
``pytest`` package on import.
"""

import os
import shutil
import subprocess
from os.path import isfile, join
from pathlib import Path

from checks.compilable import check_mutant_compilable
from checks.syntactic_equivalence import check_mutant_equivalent
from util.io import write_mutant_summary
from util.rewrite_method import rewrite_method


def _execute(project_root):
    """Run the project's tests with pytest.

    Returns True if pytest exits 0 (all tests pass) — i.e. the mutant is not
    detected and survives — and False otherwise (mutant killed, incl. collection
    or syntax errors pytest reports).
    """
    # argv list (no shell) so a config-controlled project_root cannot inject
    # shell commands and paths with spaces are handled correctly. `python -m
    # pytest` uses the active interpreter's pytest.
    command = ["python", "-m", "pytest", "-q", str(project_root)]
    try:
        result = subprocess.run(
            command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
        )
    except FileNotFoundError as exc:
        raise SystemExit(
            "Python ('python') was not found on PATH. A Python interpreter with "
            "pytest installed is required to use the 'pytest' runtool."
        ) from exc

    return result.returncode == 0


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

    mutants = [["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]]

    if not _execute(project_root):
        raise IOError(
            "The original (unmutated) project did not pass pytest, so mutants "
            "cannot be evaluated against it. Run it manually to see why: "
            f"python -m pytest {project_root}"
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

        mutant_compiles = check_mutant_compilable(original_file, language)
        mutant_output.append(mutant_compiles)

        mutant_survives = False
        if mutant_compiles:
            mutant_survives = _execute(project_root)
        mutant_output.append(str(mutant_survives))

        mutants.append(mutant_output)

    write_mutant_summary(mutants_dir, mutants)
