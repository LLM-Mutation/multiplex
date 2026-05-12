"""Generate UCAs from control description"""

from pathlib import Path

from util.io import read_input_to_str, write_ucas


def generate_ucas(model, output_dir, system_prompt):
    """Generate UCAs from control description"""
    control_diagram_path = Path(output_dir, "control_diagram.txt")
    control_diagram = read_input_to_str(control_diagram_path)

    messages = [
        {"content": system_prompt, "role": "system"},
        {"content": control_diagram, "role": "user"},
    ]

    ucas_output = model.make_request(messages)

    ucas_output_path = Path(output_dir, "ucas.csv")
    write_ucas(ucas_output_path, ucas_output)
