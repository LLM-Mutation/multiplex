import pytest
from pathlib import Path

from multiplex.checks.compilable import check_mutant_compilable


@pytest.fixture
def original_method_path():
    print(Path.cwd())
    return Path("tests/resources/original_method.java")


@pytest.fixture
def uncompilable_mutant_path():
    return Path("tests/resources/uncompilable_mutant.java")


def test_check_mutant_compiles(original_method_path):
    assert check_mutant_compilable(original_method_path)


def test_check_mutant_does_not_compile(uncompilable_mutant_path):
    assert not check_mutant_compilable(uncompilable_mutant_path)
