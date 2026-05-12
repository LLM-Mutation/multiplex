"""Controller for Basic prompt approach."""

from approach.basic.code_generator import generate_code

def main(model, output_dir, prompts):
    """Controller for Basic prompt approach"""

    generate_code(model, output_dir, prompts['basic_generate_mutants'])


def __main__(model, output_dir, prompts):
    main(model, output_dir, prompts)
