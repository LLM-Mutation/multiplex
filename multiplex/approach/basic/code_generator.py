"""Code generator for basic approach."""

import os
from pathlib import Path

from util.io import read_input_to_str, write_to_file

def _get_system_prompt(method_under_test, system_prompt, language):
    return (system_prompt +
            f"""\n
            The original {language.noun} is delimited below using ###.

            ###
            {method_under_test}
            ###
            """)


def generate_code(model, output_dir, system_prompt, language):
    """Generate mutated versions of the method."""
    method_under_test_file_path = language.original_method_path(output_dir)
    method_under_test = read_input_to_str(method_under_test_file_path)
    mutants_dir = Path(output_dir, "basic-mutants/")
    os.makedirs(mutants_dir, exist_ok=True)

    messages = [
        {"content": _get_system_prompt(method_under_test, system_prompt, language), "role": "system"}
    ]

    for count in range(0, 10):
        mutant = model.make_request(messages)
        mutant = mutant.removeprefix("```" + language.fence)
        mutant = mutant.split("```")[0]

        os.makedirs(mutants_dir, exist_ok=True)
        mutant_file_path = Path(mutants_dir, f"mutant_{str(count)}{language.extension}")
        write_to_file(mutant_file_path, mutant)
