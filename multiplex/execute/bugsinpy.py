"""BugsInPy execution backend."""

import os
import shutil
import subprocess
from os.path import isfile, join
from pathlib import Path

from checks.compilable import check_mutant_compilable
from checks.syntactic_equivalence import check_mutant_equivalent
from util.io import write_mutant_summary
from util.rewrite_method import rewrite_method

VENV_BIN = Path(".multiplex-venv", "bin")


def _pytest_cmd(project_root, output_path):
    return [str(Path(project_root, VENV_BIN, "python")), "-m", "pytest", "-q",
            str(project_root), "--ignore", str(output_path)]


def _execute(project_root, output_path, approach, label):
    """Run the suite; True if it passes (mutant survives), False if it fails."""

    venv_bin = Path(project_root, VENV_BIN)
    if not (venv_bin / "python").exists():
        raise SystemExit(
            f"No prepared virtualenv at {venv_bin}. The 'bugsinpy' runtool expects "
            "the checkout to be provisioned (venv + deps + setup) beforehand."
        )
    env = os.environ.copy()
    env["PATH"] = str(venv_bin) + os.pathsep + env.get("PATH", "")
    env["PYTHONPATH"] = (str(Path(project_root).resolve()) + os.pathsep
                         + env.get("PYTHONPATH", ""))

    cmd = _pytest_cmd(project_root, output_path)
    result = subprocess.run(cmd, cwd=str(project_root), env=env,
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    test_dir = Path(output_path, approach + "-test")
    test_dir.mkdir(parents=True, exist_ok=True)
    (test_dir / f"{label.replace(os.sep, '_')}_test.txt").write_text(
        f"$ {' '.join(cmd)}\n# exit code: {result.returncode}\n\n{result.stdout}")
    return result.returncode in (0, 5)


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
    """Execute all mutants against the checkout's test suite."""
    mutants_dir = Path(output_path, approach + "-mutants")
    mutant_files = [f for f in os.listdir(mutants_dir) if isfile(join(mutants_dir, f))]
    original_method_path = language.original_method_path(output_path)

    mutants = [["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]]

    if not _execute(project_root, output_path, approach, "ORIGINAL"):
        raise IOError(
            "The original (unmutated) project did not pass its test suite, so "
            "mutants cannot be evaluated against it. Reproduce it with:\n"
            f"  cd {project_root} && {' '.join(_pytest_cmd(project_root, output_path))}"
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
            mutant_survives = _execute(project_root, output_path, approach, mutant_file)
        mutant_output.append(str(mutant_survives))

        mutants.append(mutant_output)

    write_mutant_summary(mutants_dir, mutants)
