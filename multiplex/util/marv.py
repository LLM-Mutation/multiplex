"""Marv output helpers."""

import csv
import json
from pathlib import Path
from uuid import uuid4

from util.marv_model import MarvOutput, Mutation, MutantRegion, Pos, Status


def _read_text(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as input_file:
        return input_file.read()


def _load_statuses(mutant_summary_path: Path) -> dict[str, Status]:
    if not mutant_summary_path.exists():
        return {}

    statuses: dict[str, Status] = {}
    with open(mutant_summary_path, "r", encoding="utf-8", newline="") as summary_file:
        rows = csv.reader(summary_file)
        next(rows, None)
        for row in rows:
            if len(row) < 4:
                continue

            mutant_name, equivalent, compilable, survives = row[:4]
            if equivalent.lower() == "true":
                statuses[mutant_name] = Status.IGNORED
            elif compilable.lower() != "true":
                statuses[mutant_name] = Status.CRASHED
            elif survives.lower() == "true":
                statuses[mutant_name] = Status.SURVIVED
            else:
                statuses[mutant_name] = Status.KILLED

    return statuses


def _mutant_sort_key(mutant_file_path: Path) -> tuple[int, str]:
    suffix = mutant_file_path.stem.removeprefix("mutant_")
    try:
        return int(suffix), mutant_file_path.name
    except ValueError:
        return 0, mutant_file_path.name


def _load_operations(output_dir: Path, approach: str, mutant_files: list[Path]) -> dict[str, str]:
    if approach != "hazop":
        return {}

    mutated_descriptions_path = Path(output_dir, "hazop-mutated-descriptions.txt")
    if not mutated_descriptions_path.exists():
        return {}

    guidewords: list[str] = []
    with open(mutated_descriptions_path, "r", encoding="utf-8", newline="") as descriptions_file:
        rows = csv.reader(descriptions_file)
        for row in rows:
            if len(row) < 3:
                continue
            guidewords.append(row[2].strip())

    operations: dict[str, str] = {}
    for mutant_file_path, guideword in zip(sorted(mutant_files, key=_mutant_sort_key), guidewords):
        operations[mutant_file_path.name] = guideword or "REPLACE_METHOD"

    return operations


def _file_span(text: str) -> tuple[Pos, Pos]:
    lines = text.splitlines()
    if not lines:
        return Pos(Line=0, Char=0), Pos(Line=0, Char=0)

    end_line = len(lines) - 1
    end_char = len(lines[-1])
    return Pos(Line=0, Char=0), Pos(Line=end_line, Char=end_char)


def _marv_line(line: int) -> int:
    return line


def output_marv(output_dir, approach):
    output_dir = Path(output_dir)
    original_method_path = Path(output_dir, "original_method.java")
    mutants_dir = Path(output_dir, f"{approach}-mutants")
    mutant_summary_path = Path(mutants_dir, "mutant_summary.csv")
    marv_output_path = Path(output_dir, "marv.json")

    if not original_method_path.exists() or not mutants_dir.exists():
        raise FileNotFoundError(
            "Cannot create Marv output because the mutants outputs are missing."
        )

    original_method = _read_text(original_method_path)
    start, end = _file_span(original_method)
    statuses = _load_statuses(mutant_summary_path)
    mutant_files = list(mutants_dir.glob("mutant_*.java"))
    operations = _load_operations(output_dir, approach, mutant_files)

    mutations = []
    for mutant_file_path in sorted(mutant_files, key=_mutant_sort_key):
        mutant_name = mutant_file_path.name
        mutant_source = _read_text(mutant_file_path)
        status = statuses.get(mutant_name, Status.PENDING)

        mutations.append(
            Mutation(
                ID=str(uuid4()),
                Description=f"{approach.upper()} mutant generated from {mutant_name}",
                Operation=operations.get(mutant_name, "REPLACE_METHOD"),
                Start=start,
                End=end,
                Status=status,
                Replacement=mutant_source,
                FrameworkMutantID=mutant_name.removesuffix(".java"),
            )
        )

    marv_output = MarvOutput(
        files={
            "original_method.java": [
                MutantRegion(
                    ID=str(uuid4()),
                    StartLine=_marv_line(0),
                    EndLine=end.Line,
                    Mutations=mutations,
                )
            ]
        }
    )

    payload = {
        file_path: [
            {
                "ID": region.ID,
                "StartLine": region.StartLine,
                "EndLine": region.EndLine,
                "Mutations": [
                    {
                        "ID": mutation.ID,
                        "Description": mutation.Description,
                        "Operation": mutation.Operation,
                        "Start": {"Line": _marv_line(mutation.Start.Line), "Char": mutation.Start.Char},
                        "End": {"Line": _marv_line(mutation.End.Line), "Char": mutation.End.Char},
                        "Status": mutation.Status.value,
                        "Replacement": mutation.Replacement,
                        "FrameworkMutantID": mutation.FrameworkMutantID,
                    }
                    for mutation in region.Mutations
                ],
            }
            for region in regions
        ]
        for file_path, regions in marv_output.files.items()
    }

    with open(marv_output_path, "w", encoding="utf-8") as output_file:
        json.dump(payload, output_file, indent=2)