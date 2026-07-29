"""Controller for Systems Theoretic Process Analysis (STPA)"""

from approach.stpa.code_generator import generate_code
from approach.stpa.control_diagram import create_control_diagram
from approach.stpa.uca_generator import generate_ucas


def main(model, output_dir, prompts, language):
    """Controller for Systems Theoretic Process Analysis (STPA)"""

    create_control_diagram(model, output_dir, prompts['stpa_describe_control_flow'], language)
    generate_ucas(model, output_dir, prompts['stpa_identify_ucas'])
    generate_code(model, output_dir, prompts['stpa_implement_ucas'], language)


def __main__(model, output_dir, prompts, language):
    main(model, output_dir, prompts, language)
