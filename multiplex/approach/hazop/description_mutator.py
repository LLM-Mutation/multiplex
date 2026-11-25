"""Ask LLM to apply HAZOP guideword based mutation to descriptions."""

import csv
import re
from pathlib import Path
from util.io import read_input_to_str, write_to_file


GUIDEWORDS = {
    "NO", "NOT", "NONE", "MORE", "MORE OF", "HIGHER", "LESS", "LESS OF", "LOWER", "AS WELL AS", "MORE THAN",
    "PART OF", "REVERSE", "OTHER THAN", "OTHER",
}
NUMBER = re.compile(r'["\s]*(\d+)\.?"?(?=[,\s])')


def _unquote(text):
    text = text.strip()
    if text.endswith('"') and (text.startswith('"') or text.count('"') % 2):
        text = text[:-1]
    return text.removeprefix('"').replace('""', '"').strip()


def parse_deviation(line):
    """[number, original_rule, guideword, changed_rule], or None if the line has no such parts."""
    number = NUMBER.match(line)
    if not number:
        return None

    fields = line[number.end():].split(",")
    for i, field in enumerate(fields):
        if field.strip(' \t\r"') not in GUIDEWORDS:
            continue
        before = fields[:i]
        while before and not before[-1].strip(' \t"'):
            before.pop()
        original = _unquote(",".join(before).lstrip(", \t"))
        changed = _unquote(",".join(fields[i + 1:]).strip(", \t\r\n"))
        if original and changed:
            return [number[1], original, field.strip(' \t\r"'), changed]
    return None


def mutate_descriptions(model, output_dir, system_prompt):
    descriptions_path = Path(output_dir, "hazop-descriptions.txt")
    descriptions = read_input_to_str(descriptions_path)

    user_prompt = descriptions

    messages = [
        {"content": system_prompt, "role": "system"},
        {"content": user_prompt, "role": "user"}
    ]

    mutated_descriptions_output = model.make_request(messages)

    mutate_descriptions_output_path = Path(output_dir, "hazop-mutated-descriptions.txt")

    write_to_file(Path(output_dir, "hazop-mutated-descriptions-raw.txt"), mutated_descriptions_output)

    for line in mutated_descriptions_output.split("\n"):
        if not line.strip():
            continue

        row = parse_deviation(line)
        if row:
            with open(
                    mutate_descriptions_output_path, mode="a", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow(row)

        else:
            print(f"Unexpected format: {line}")
