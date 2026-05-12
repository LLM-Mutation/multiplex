from pathlib import Path
from util.io import read_input_to_str


def get_method_under_test(output_dir):
    method_under_test_path = Path(output_dir, "original_method.java")
    method_under_test = read_input_to_str(method_under_test_path)
    if method_under_test is not None:
        return method_under_test

    raise FileNotFoundError(f"ERROR: No method in {method_under_test_path}")
