"""Generate control description from method"""

from pathlib import Path

from approach.util import get_method_under_test
from util.io import write_to_file


def create_control_diagram(model, output_dir, system_prompt):
    """Create control description from method"""
    user_prompt = get_method_under_test(output_dir)
    messages = [
        {"content": system_prompt, "role": "system"},
        {"content": user_prompt, "role": "user"},
    ]

    control_diagram = model.make_request(messages)

    control_diagram_output_path = Path(output_dir, "control_diagram.txt")
    write_to_file(control_diagram_output_path, control_diagram)
