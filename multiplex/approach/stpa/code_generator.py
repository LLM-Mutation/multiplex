"""Generate mutants from UCAs"""

import os
from pathlib import Path

from util.io import read_input_to_str, read_ucas, write_to_file


def _get_system_prompt(method_under_test, system_prompt):
    return (system_prompt +
            f"""\n
            The original Java Method is delimited below using ###.

            ###
            {method_under_test}
            ###
            """)


def generate_code(model, output_dir, system_prompt):
    """Generate mutants from UCAs"""
    uca_file_path = Path(output_dir, "ucas.csv")
    method_under_test_file_path = Path(output_dir, "original_method.java")
    ucas, ucas_count = read_ucas(uca_file_path)
    method_under_test = read_input_to_str(method_under_test_file_path)

    mutants_dir = Path(output_dir, "stpa-mutants/")

    messages_orig = [
        {"content": _get_system_prompt(method_under_test, system_prompt), "role": "system"}
    ]

    for count in range(0, ucas_count - 1):
        messages = messages_orig.copy()
        user_prompt = f"{ucas[count]}"
        messages.append({"content": user_prompt, "role": "user"})

        mutant = model.make_request(messages)
        mutant = mutant.removeprefix("```java")
        mutant = mutant.split("```", 1)[0]

        os.makedirs(mutants_dir, exist_ok=True)
        mutant_file_path = Path(mutants_dir, f"mutant_{str(count)}.java")
        write_to_file(mutant_file_path, mutant)
