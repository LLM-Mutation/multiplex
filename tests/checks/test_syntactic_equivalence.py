import pytest
from pathlib import Path

from multiplex.checks.syntactic_equivalence import check_mutant_equivalent


@pytest.fixture
def original_method_path():
    return Path("tests/resources/original_method.java")

@pytest.fixture
def equivalent_mutant_path():
    return Path("tests/resources/equivalent_mutant.java")

@pytest.fixture
def killed_mutant_path():
    return Path("tests/resources/killed_mutant.java")


def test_check_mutant_equivalent_is_equivalent(equivalent_mutant_path, original_method_path):
    """Check mutant identified as equivalent."""
    assert check_mutant_equivalent(equivalent_mutant_path, original_method_path)


def test_check_mutant_equivalent_not_equivalent(killed_mutant_path, original_method_path):
    """Check mutant identified as not equivalent."""
    assert not check_mutant_equivalent(killed_mutant_path, original_method_path)
