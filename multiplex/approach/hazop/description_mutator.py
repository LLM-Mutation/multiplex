"""Ask LLM to apply HAZOP guideword based mutation to descriptions."""

import csv
import re
from pathlib import Path
from util.io import read_input_to_str, write_to_file


DEVIATION = re.compile(
    r'^["\s]*(?P<number>\d+)[."\s]*[,\s]\s*(?P<original>.+?)\s*(?:,\s*(?:"")?\s*)+"?\s*'
    r'(?P<guideword>NO|NOT|NONE|MORE|MORE OF|HIGHER|LESS|LESS OF|LOWER|AS WELL AS|MORE THAN|PART OF|REVERSE'
    r'|OTHER THAN|OTHER)["\s]*,[\s,]*(?P<changed>.+?)\s*$'
)


def _unquote(text):
    text = text.strip()
    if text.endswith('"') and (text.startswith('"') or text.count('"') % 2):
        text = text[:-1]
    return text.removeprefix('"').replace('""', '"').strip()


def parse_deviation(line):
    """[number, original_rule, guideword, changed_rule], or None if the line has no such parts."""
    match = DEVIATION.match(line)
    if not match:
        return None
    changed = _unquote(match["changed"])
    if not changed:
        return None
    return [match["number"], _unquote(match["original"]), match["guideword"], changed]


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
