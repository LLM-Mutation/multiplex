import os
import shutil
import subprocess
from os.path import isfile, join
from pathlib import Path

from checks.compilable import check_mutant_compilable
from util.rewrite_method import rewrite_method


def _execute_mutant(project_root):
    """Execute the mutated code"""
    result = ""
    command = f"mvn -f {project_root} clean test"

    try:
        result = subprocess.check_output(
            command, shell=True, executable="/bin/bash", stderr=subprocess.STDOUT
        )

    except subprocess.CalledProcessError as cpe:
        result = cpe.output

    finally:
        for line in result.splitlines():
            if "BUILD SUCCESS" in line.decode():
                print("Surviving mutant")
                break


def run_mutants(
    project_root,
    filename,
    output_path,
    method_start_byte,
    method_end_byte,
    duplicate,
    approach,
):
    """Execute all mutants using Maven build."""
    mutants_path = Path(output_path, approach + "-mutants")
    mutant_files = [
        f for f in os.listdir(mutants_path) if isfile(join(mutants_path, f))
    ]

    for file in mutant_files:
        if duplicate.exists():
            shutil.copy2(duplicate, filename)

        path = Path(mutants_path, file)
        rewrite_method(filename, output_path, method_start_byte, method_end_byte, path)

        mutant_compiles = check_mutant_compilable(filename)
        if mutant_compiles:
            check_mutant_compilable(project_root)

        else:
            print(f"Mutant {file} does not compile")
