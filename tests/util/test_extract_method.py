import os
import tempfile
import pytest  # noqa: F401
from multiplex.util.extract_method import extract_method_from_file

# --- Tests constructed using OpenCode Assistant with GPT-4.1 ---

@pytest.fixture
def java_constructor_code():
    return '''
public class Example {
    public Example() {
        // constructor body
    }
    public void foo() {}
}
'''

def test_extracts_constructor_by_name_and_line(java_constructor_code):
    code = java_constructor_code
    print(code)
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "Example.java")
        with open(src_path, "w") as f:
            f.write(code)
        # Constructor name is 'Example', line is 2 (1-based)
        result = extract_method_from_file(src_path, "Example", tmpdir, start_line=3)
        assert result is not None, "Should extract constructor declaration"
        start, end = result
        with open(os.path.join(tmpdir, "original_method.java")) as f:
            extracted = f.read()
        assert "public Example()" in extracted
        assert "constructor body" in extracted


def test_does_not_extract_nonexistent_constructor(java_constructor_code):
    code = java_constructor_code
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "Example.java")
        with open(src_path, "w") as f:
            f.write(code)
        # Wrong name
        result = extract_method_from_file(src_path, "Nonexistent", tmpdir, start_line=2)
        assert result is None, "Should not extract if constructor name does not match"


def test_extracts_method_not_constructor(java_constructor_code):
    code = java_constructor_code
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "Example.java")
        with open(src_path, "w") as f:
            f.write(code)
        # Method name is 'foo', line is 5 (1-based)
        result = extract_method_from_file(src_path, "foo", tmpdir, start_line=6)
        assert result is not None, "Should extract method declaration"
        start, end = result
        with open(os.path.join(tmpdir, "original_method.java")) as f:
            extracted = f.read()
        assert "public void foo()" in extracted

# --- End generated tests ---
