"""Asks LLM to generate a step by step description of the input method."""

from pathlib import Path

from approach.util import get_method_under_test
from util.io import write_to_file


def describe_method(model, output_dir, system_prompt):
    """Describe the method."""
    user_prompt = get_method_under_test(output_dir)

    messages = [
        {"content": system_prompt, "role": "system"},
        {"content": user_prompt, "role": "user"}
    ]

    descriptions = model.make_request(messages)

    descriptions_output_path = Path(output_dir, "hazop-descriptions.txt")
    write_to_file(descriptions_output_path, descriptions)
