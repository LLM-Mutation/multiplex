"""Parser methods for LLM Yaml output."""

import yaml


def parse_output(input):
    """Parse expected yaml output from LLM."""
    input = input.removeprefix("```yaml").removesuffix("```")
    try:
        output = yaml.safe_load(input)
        print(output)
        return output
    except yaml.YAMLError:
        print("Could not parse LLM output")
        return None


def add_mutant_to_method(numbered_src, mutant, line_number):
    """Place mutant in method, preserving indentation."""
    lines = numbered_src.split("\n")
    method = []
    for i, line in enumerate(lines):
        prefix = f"{str(i+1)}: "
        if line.startswith(prefix):
            content = line[len(prefix) :]
            if (i + 1) == line_number:
                indentation = len(content) - len(content.lstrip())
                mutant_line = " " * indentation + mutant.lstrip()
                method.append(mutant_line)
            else:
                method.append(content)
        else:
            method.append(line)
    return "\n".join(method)
