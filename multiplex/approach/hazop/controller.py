"""Controller for HAZOP"""

# from approach.hazop.code_generator import generate_code
from approach.hazop.description_mutator import mutate_descriptions
from approach.hazop.method_explainer import describe_method
from approach.hazop.code_generator import generate_code


def main(model, output_dir, prompts):
    """Controller for HAZOP"""

    describe_method(model, output_dir, prompts['hazop_describe_process'])
    mutate_descriptions(model, output_dir, prompts['hazop_identify_deviations'])
    generate_code(model, output_dir, prompts['hazop_implement_deviations'])


def __main__(model, output_dir, prompts):
    main(model, output_dir, prompts)
