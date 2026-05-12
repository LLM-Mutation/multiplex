import os
import shutil
import subprocess
import time
from os.path import isfile, join
from pathlib import Path

from checks.compilable import check_mutant_compilable
from checks.syntactic_equivalence import check_mutant_equivalent
from util.io import write_mutant_summary
from util.rewrite_method import rewrite_method


def _execute(project_root, file=None, approach=None, timer=None):
    """Execute the mutated code"""
    result = ""

    command1 = ["rm", "-r", f"{project_root}/.classes_instrumented", f"{project_root}/target"]
    kill_threads_command = ["pkill", "-f", "java.*$(pwd)"]
    try:
        subprocess.run(command1, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        pass
    command2 = ["defects4j", "test", "-w", f"{project_root}"]
    try:
        _env = os.environ.copy()
        _env["PATH"] = f"{_env['PATH']}:./defects4j/framework/bin"
        _env["JAVA_HOME"] = _env["JDK_11"]
        if timer:
            result = subprocess.run(command2, capture_output=True, text=True, env=_env, timeout=timer)
            test_output_dir = Path(f"{project_root}/output/{approach}-test/")
            test_output_dir.mkdir(parents=True, exist_ok=True)
            test_results_file_path = Path(
                test_output_dir, f"{file.removesuffix('.java')}_test.txt"
            )
            with open(test_results_file_path, "w") as f:
                f.write(result.stderr + result.stdout)
        else:
            result = subprocess.run(command2, capture_output=True, text=True, env=_env)
        print(result)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        try: 
            subprocess.run(kill_threads_command, capture_output=True, text=True, env=_env)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
            pass
        return False
    try: 
        subprocess.run(kill_threads_command, capture_output=True, text=True, env=_env)
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        pass


    for line in result.stdout.splitlines():
        if "Failing tests: 0" in line:
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
    """Execute all mutants using Defects4J build."""
    mutants_dir = Path(output_path, approach + "-mutants")
    mutant_files = [f for f in os.listdir(mutants_dir) if isfile(join(mutants_dir, f))]
    original_method_path = Path(output_path, "original_method.java")

    mutants = []
    header = ["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]
    mutants.append(header)

    start = time.perf_counter()
    success = _execute(project_root)
    end = time.perf_counter()
    timer = end - start
    print("Timeout timer:", timer * 5)

    if not success:
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
            mutant_survives = _execute(project_root, mutant_file, approach, timer=timer * 5)
        mutant_output.append(str(mutant_survives))

        mutants.append(mutant_output)

    write_mutant_summary(mutants_dir, mutants)
