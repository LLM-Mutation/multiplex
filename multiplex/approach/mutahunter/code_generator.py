"""Code generator for mutahunter approach."""

import os
from pathlib import Path
from tree_sitter import Language, Parser
import tree_sitter_java as ts_java

from util.parser import add_mutant_to_method, parse_output
from util.io import read_input_to_str, write_to_file


def _get_system_prompt(method_under_test, system_prompt):
    return (
        system_prompt
        + f"""\n
            The original Java Method is delimited below using ###.

            ###
            {method_under_test}
            ###
            """
    )


def _get_user_prompt(ast, src_code_file, language, numbered_src_code):
    # NOTE: USER MUST COLLECT MUTAHUNTER PROMPTS THEMSELVES DUE TO LICENSING
    user_prompt = f"""
     {src_code_file}
    ```{language}
    {numbered_src_code}
    ```

     {src_code_file}
     {language} 
    """

    if ast is not None:
        return (
            f"""
        ```ast
        {ast}
        ```"""
            + user_prompt
        )
    return user_prompt


def _get_ast(method_under_test):
    """Get ast of method."""
    bytestring = bytes(method_under_test.encode("utf-8"))
    language = Language(ts_java.language())
    parser = Parser(language)
    tree = parser.parse(bytestring, encoding="utf8")
    return str(tree.root_node)


def _get_numbered_src_code(method_under_test):
    """Get numbered src_code for mutahunter prompt."""
    lines = method_under_test.split("\n")
    numbered_lines = [f"{i+1}: {line}" for i, line in enumerate(lines)]
    numbered_src_code = "\n".join(numbered_lines)
    return numbered_src_code


def generate_code(model, output_dir, system_prompt):
    """Generate mutated versions of the method."""
    method_under_test_file_path = Path(output_dir, "original_method.java")
    method_under_test = read_input_to_str(method_under_test_file_path)
    mutants_dir = Path(output_dir, "mutahunter-mutants/")
    os.makedirs(mutants_dir, exist_ok=True)

    ast = _get_ast(method_under_test)
    src_code_file = method_under_test_file_path
    language = "Java"
    numbered_src_code = _get_numbered_src_code(method_under_test)

    messages = [
        {
            "content": _get_system_prompt(method_under_test, system_prompt),
            "role": "system",
        },
        {
            "content": _get_user_prompt(
                ast, src_code_file, language, numbered_src_code
            ),
            "role": "user",
        },
    ]

    mutant_output = model.make_request(messages)
    mutant_info = parse_output(mutant_output)
    if mutant_info is not None:

        for count, mutant_yaml in enumerate(mutant_info["mutants"]):
            mutant = add_mutant_to_method(
                numbered_src_code,
                mutant_yaml["mutated_code"],
                mutant_yaml["line_number"],
            )

            mutant_file_path = Path(mutants_dir, f"mutant_{str(count)}.java")
            write_to_file(mutant_file_path, mutant)
