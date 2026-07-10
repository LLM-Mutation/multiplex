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
    """Run the project's tests with Maven.

    Returns True if the build passes (all tests green) — i.e. the mutant is not
    detected and survives — and False if the build/tests fail (mutant killed).
    """
    command = f"mvn -f {project_root} clean test"
    try:
        result = subprocess.check_output(
            command, shell=True, executable="/bin/bash", stderr=subprocess.STDOUT
        )
    except subprocess.CalledProcessError as cpe:
        result = cpe.output

    for line in result.splitlines():
        if "BUILD SUCCESS" in line.decode():
            return True
    return False


def run_mutants(
    project_root,
    original_file,
    output_path,
    method_start_byte,
    method_end_byte,
    duplicate,
    approach,
):
    """Execute all mutants using a Maven build."""
    mutants_dir = Path(output_path, approach + "-mutants")
    mutant_files = [f for f in os.listdir(mutants_dir) if isfile(join(mutants_dir, f))]
    original_method_path = Path(output_path, "original_method.java")

    mutants = [["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]]

    if not _execute(project_root):
        raise IOError("EXCEPTION: Original code has failing tests")

    for mutant_file in mutant_files:
        mutant_output = [mutant_file]
        print("Evaluating Mutant: ", mutant_file)
        if duplicate.exists():
            shutil.copy2(duplicate, original_file)

        path = Path(mutants_dir, mutant_file)
        mutant_equivalent = check_mutant_equivalent(path, original_method_path)
        mutant_output.append(mutant_equivalent)

        rewrite_method(original_file, method_start_byte, method_end_byte, path)

        mutant_compiles = check_mutant_compilable(original_file)
        mutant_output.append(mutant_compiles)

        mutant_survives = False
        if mutant_compiles:
            mutant_survives = _execute(project_root)
        mutant_output.append(str(mutant_survives))

        mutants.append(mutant_output)

    write_mutant_summary(mutants_dir, mutants)
