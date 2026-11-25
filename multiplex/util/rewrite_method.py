"""Rewrite mutated method in original code file"""

from pathlib import Path

from util.io import read_input_to_str, write_to_file
from util.reindent import reindent


def rewrite_method(orig_path, start_byte, end_byte, mutant_file_path, language=None):
    """Rewrite mutated method in original code file"""
    # duplicate original code file
    duplicate_path = Path(orig_path + ".orig")
    original_code = duplicate_path.read_text(encoding="utf-8")

    new_method_call_code = str(read_input_to_str(mutant_file_path)).strip()
    if language is not None and language.name == "python":
        new_method_call_code = reindent(original_code, start_byte, new_method_call_code)
    modified_code = (
        original_code[:start_byte] + new_method_call_code + original_code[end_byte:]
    )

    write_to_file(orig_path, modified_code)
