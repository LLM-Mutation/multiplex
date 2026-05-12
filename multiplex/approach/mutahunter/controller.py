"""Controller for mutahunter prompt approach."""

from approach.mutahunter.code_generator import generate_code

def main(model, output_dir, prompts):
    """Controller for Mutahunter prompt approach"""

    generate_code(model, output_dir, prompts['mutahunter_generate_mutants'])


def __main__(model, output_dir, prompts):
    main(model, output_dir, prompts)
