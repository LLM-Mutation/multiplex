import pytest
from pathlib import Path

from multiplex.checks.compilable import check_mutant_compilable
from multiplex.languages import get_language

JAVA = get_language("java")
PYTHON = get_language("python")


@pytest.fixture
def original_method_path():
    print(Path.cwd())
    return Path("tests/resources/original_method.java")


@pytest.fixture
def uncompilable_mutant_path():
    return Path("tests/resources/uncompilable_mutant.java")


def test_check_mutant_compiles(original_method_path):
    assert check_mutant_compilable(original_method_path, JAVA)


def test_check_mutant_does_not_compile(uncompilable_mutant_path):
    assert not check_mutant_compilable(uncompilable_mutant_path, JAVA)


# --- Python ---


def test_python_valid_source_compiles(tmp_path):
    p = tmp_path / "m.py"
    p.write_text("def f(n):\n    return n + 1\n")
    assert check_mutant_compilable(p, PYTHON)


@pytest.mark.parametrize(
    "code",
    [
        "def f(n):\n    return foo(n",   # unclosed paren
        "def f(n)\n    return n",         # missing colon
        "def f(n):\n    return n +* 2",   # bad operator
    ],
)
def test_python_syntax_error_does_not_compile(tmp_path, code):
    p = tmp_path / "m.py"
    p.write_text(code)
    assert not check_mutant_compilable(p, PYTHON)
