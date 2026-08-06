import os
import tempfile
import pytest  # noqa: F401
from multiplex.util.extract_method import extract_method_from_file
from multiplex.languages import get_language

JAVA = get_language("java")
PYTHON = get_language("python")

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
        result = extract_method_from_file(src_path, "Example", tmpdir, 3, JAVA)
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
        result = extract_method_from_file(src_path, "Nonexistent", tmpdir, 2, JAVA)
        assert result is None, "Should not extract if constructor name does not match"


def test_extracts_method_not_constructor(java_constructor_code):
    code = java_constructor_code
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "Example.java")
        with open(src_path, "w") as f:
            f.write(code)
        # Method name is 'foo', line is 5 (1-based)
        result = extract_method_from_file(src_path, "foo", tmpdir, 6, JAVA)
        assert result is not None, "Should extract method declaration"
        start, end = result
        with open(os.path.join(tmpdir, "original_method.java")) as f:
            extracted = f.read()
        assert "public void foo()" in extracted

# --- End generated tests ---


# --- Python extraction ---

PYTHON_CODE = '''\
def helper(x):
    return x + 1


def classify(n):
    if n > 0:
        return 1
    return 0
'''


def test_extracts_python_function_by_name_and_line():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "mod.py")
        with open(src_path, "w") as f:
            f.write(PYTHON_CODE)
        # 'classify' identifier is on line 5 (1-based)
        result = extract_method_from_file(src_path, "classify", tmpdir, 5, PYTHON)
        assert result is not None, "Should extract Python function"
        with open(os.path.join(tmpdir, "original_method.py")) as f:
            extracted = f.read()
        assert extracted.startswith("def classify(n):")
        assert "return 1" in extracted
        # must not spill into the following/preceding function
        assert "helper" not in extracted


def test_python_line_must_match():
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "mod.py")
        with open(src_path, "w") as f:
            f.write(PYTHON_CODE)
        # correct name, wrong line
        result = extract_method_from_file(src_path, "classify", tmpdir, 1, PYTHON)
        assert result is None
