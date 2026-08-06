"""Ask LLM to generate mutants based on mutated descriptions."""

import os
from pathlib import Path

from util.io import read_hazop_mutations, read_input_to_str, write_to_file


def _get_system_prompt(method_under_test, system_prompt, language):
    return (system_prompt +
            f"""\n
            The original {language.noun} is delimited below using ###.

            ###
            {method_under_test}
            ###
            """)


def generate_code(model, output_dir, system_prompt, language):
    """Generate code for each mutant."""

    mutate_descriptions_output_path = Path(output_dir, "hazop-mutated-descriptions.txt")
    mutated_descriptions, count = read_hazop_mutations(mutate_descriptions_output_path)

    original_method_path = language.original_method_path(output_dir)
    original_method = read_input_to_str(original_method_path)

    mutants_dir = Path(output_dir, "hazop-mutants/")

    messages_orig = [
        {"content": _get_system_prompt(original_method, system_prompt, language), "role": "system"},
    ]

    count = 0
    for desc in mutated_descriptions:
        messages = messages_orig.copy()
        user_prompt = f"{desc}"
        messages.append({"content": user_prompt, "role": "user"})

        mutant = model.make_request(messages)
        mutant = mutant.removeprefix("```" + language.fence)
        mutant = mutant.split("```", 1)[0]

        os.makedirs(mutants_dir, exist_ok=True)
        mutant_file_path = Path(mutants_dir, f"mutant_{str(count)}{language.extension}")
        write_to_file(mutant_file_path, mutant)
        count += 1
