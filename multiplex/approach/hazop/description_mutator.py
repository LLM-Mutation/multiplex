"""Ask LLM to apply HAZOP guideword based mutation to descriptions."""

import csv
from pathlib import Path
from util.io import read_input_to_str


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

    lines = mutated_descriptions_output.split("\n")

    for line in lines:
        parts = line.split(",")
        if len(parts) >= 4:
            line_number, original_rule, guideword, changed_rule = (
                parts[0].strip().removeprefix('"""').removesuffix('"""'),
                parts[1].strip().removeprefix('"""').removesuffix('"""'),
                parts[2].strip().removeprefix('"""').removesuffix('"""'),
                parts[3].strip().removeprefix('"""').removesuffix('"""'),
            )

            with open(
                    mutate_descriptions_output_path, mode="a", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)
                writer.writerow([line_number, original_rule, guideword, changed_rule])

        else:
            print(f"Unexpected format: {mutated_descriptions_output}")
