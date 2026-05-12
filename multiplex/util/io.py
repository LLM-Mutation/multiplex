"""Input/Output Helper Methods"""

import csv
import os
from pathlib import Path
import shutil


def write_to_file(output_file_path, output):
    """General write output to file."""
    with open(output_file_path, "w") as output_file:
        output_file.write(output)


def write_ucas(ucas_output_path, ucas_output):
    """Write Unsafe Control Actions to file."""
    with open(ucas_output_path, "w") as f:
        [f.write(f"{line}\n") for line in ucas_output.strip().split("\n")]


def write_mutant_summary(mutants_dir, mutants):
    """Write mutant summaries to file."""
    mutant_summary_path = Path(mutants_dir, "mutant_summary.csv")

    with open(mutant_summary_path, "w") as msp:
        write = csv.writer(msp)
        write.writerows(mutants)


def read_input_to_str(input_file_path):
    """General read input file."""
    with open(input_file_path, "r") as input_file:
        return input_file.read()


def read_ucas(input_file_path):
    """Read Unsafe Control Actions from file."""
    with open(input_file_path, "r") as f:
        ucas = f.readlines()
        ucas_count = len(ucas)
    return ucas, ucas_count


def read_hazop_mutations(input_file_path):
    """Read Hazop Mutated Descriptions from file."""
    with open(input_file_path, "r") as f:
        lines = f.readlines()
        lines_count = len(lines)
    mutated_descriptions = [line.split(",")[3] for line in lines]
    return mutated_descriptions, lines_count


def reset_source_code(duplicate_file_path, filename):
    """Copy duplicate back to original file."""
    if duplicate_file_path.exists():
        os.remove(filename)
        os.rename(duplicate_file_path, filename)
    shutil.copy2(filename, duplicate_file_path)
