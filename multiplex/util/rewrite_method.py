"""Rewrite mutated method in original code file"""

from pathlib import Path

from util.io import read_input_to_str, write_to_file


def rewrite_method(orig_path, start_byte, end_byte, mutant_file_path):
    """Rewrite mutated method in original code file"""
    # duplicate original code file
    duplicate_path = Path(orig_path + ".orig")
    original_code = duplicate_path.read_text(encoding="utf-8")

    new_method_call_code = str(read_input_to_str(mutant_file_path)).strip()
    modified_code = (
        original_code[:start_byte] + new_method_call_code + original_code[end_byte:]
    )

    write_to_file(orig_path, modified_code)
