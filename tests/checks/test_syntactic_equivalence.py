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


def _write(tmp_path, name, code):
    p = tmp_path / name
    p.write_text(code)
    return p


def test_string_literal_change_is_not_equivalent(tmp_path):
    """A changed string literal (same AST shape) must not be equivalent."""
    original = _write(tmp_path, "o.java", 'String f() { return "negative"; }')
    mutant = _write(tmp_path, "m.java", 'String f() { return "positive"; }')
    assert not check_mutant_equivalent(mutant, original)


def test_numeric_literal_change_is_not_equivalent(tmp_path):
    original = _write(tmp_path, "o.java", "int f() { return 1; }")
    mutant = _write(tmp_path, "m.java", "int f() { return 2; }")
    assert not check_mutant_equivalent(mutant, original)


def test_identifier_change_is_not_equivalent(tmp_path):
    original = _write(tmp_path, "o.java", "int f(int a, int b) { return a; }")
    mutant = _write(tmp_path, "m.java", "int f(int a, int b) { return b; }")
    assert not check_mutant_equivalent(mutant, original)


def test_comment_only_change_is_equivalent(tmp_path):
    """Differences only in comments/whitespace remain equivalent."""
    original = _write(tmp_path, "o.java", "int f() { return 1; }")
    mutant = _write(tmp_path, "m.java", "int f() {\n    // added comment\n    return 1;\n}")
    assert check_mutant_equivalent(mutant, original)


def test_identical_source_is_equivalent(tmp_path):
    original = _write(tmp_path, "o.java", "int f() { return 1; }")
    mutant = _write(tmp_path, "m.java", "int f() { return 1; }")
    assert check_mutant_equivalent(mutant, original)
