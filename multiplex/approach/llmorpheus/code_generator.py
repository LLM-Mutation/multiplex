import json
from pathlib import Path
from approach.util import get_method_under_test
from util.io import write_to_file
from model import Model
import re


def _user_prompt(code: str, orig: str):
    return f"""
    Your task is to apply mutation testing to the following code:
    ```
    {code}
    ```

    by replacing the PLACEHOLDER with a buggy code fragment that has different
    behavior than the original code fragment, which was:
    ```
    {orig}
    ```
    Please consider changes such as using different operators, changing constants,
    referring to different variables, object properties, functions, or methods.  

    Provide three answers as fenced code blocks containing a single line of code,
    using the following template:

    Option 1: The PLACEHOLDER can be replaced with:
    ```
    <code fragment>
    ```
    This would result in different behavior because <brief explanation>.

    Option 2: The PLACEHOLDER can be replaced with:
    ```
    <code fragment>
    ```
    This would result in different behavior because <brief explanation>.

    Option 3: The PLACEHOLDER can be replaced with:
    ```
    <code fragment>
    ```
    This would result in different behavior because <brief explanation>.

    Please conclude your response with "DONE."
    """


def generate_code(model: Model, output_dir: Path, llmorpheus_system: str):
    placeholder_dir = Path(output_dir, "placeholders")
    mutants_dir = Path(output_dir, "llmorpheus-mutants/")
    mutants_dir.mkdir(parents=True, exist_ok=True)

    placeholders_json = Path(placeholder_dir, "placeholders.json")
    with placeholders_json.open("r", encoding="utf-8") as f:
        locations = json.load(f)
    if not isinstance(locations, dict):
        raise ValueError("Expected a JSON object at the top level.")

    placeholders_count = len(list(placeholder_dir.glob("*_placeholder.java")))

    mutant_number = 0
    for count in range(0, placeholders_count):
        p_f = f"{count}_placeholder.java"
        p_fn = Path(placeholder_dir, p_f)
        orig_p_fn = Path(placeholder_dir, f"{count}_orig.java")

        with open(p_fn, "r") as pf:
            p = pf.read()
        with open(orig_p_fn, "r") as opf:
            orig_p = opf.read()

        messages = [
            {"content": llmorpheus_system, "role": "system"},
            {"content": _user_prompt(p, orig_p), "role": "user"},
        ]

        response = model.make_request(messages)

        matches = re.findall(r"\n```\n(.*?)\n```", response, re.DOTALL)

        for mutant_code in matches:

            mutant_file_path = Path(mutants_dir, f"mutant_{str(mutant_number)}.java")

            start_byte = locations[p_f]["start_byte"]
            end_byte = locations[p_f]["end_byte"]
            method_under_test = get_method_under_test(output_dir)
            code_bytes = method_under_test.encode()
            mutant = (
                code_bytes[:start_byte] + mutant_code.encode() + code_bytes[end_byte:]
            ).decode()

            write_to_file(mutant_file_path, mutant)
            mutant_number += 1
