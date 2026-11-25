"""HAZOP deviations must survive the line formats that LLMs reply with."""

import time

import pytest

from approach.hazop.description_mutator import mutate_descriptions, parse_deviation
from util.io import read_hazop_mutations


@pytest.mark.parametrize("line", [
    "1, checks a, REVERSE, checks b",
    "1. checks a, REVERSE, checks b",
    "1., checks a, REVERSE, checks b",
    '"1, checks a, REVERSE, checks b"',
    '"1", "checks a", "REVERSE", "checks b"',
    '1,"checks a","REVERSE","checks b"',
    "1, checks a,, REVERSE, checks b",
    '1.,"checks a","",REVERSE,"checks b"',
])
def test_formats(line):
    assert parse_deviation(line) == ["1", "checks a", "REVERSE", "checks b"]


def test_commas_in_both_rules():
    assert parse_deviation("24. if e, E or f, MORE, if e, E, or d") == [
        "24", "if e, E or f", "MORE", "if e, E, or d"]


def test_inner_quotes_are_kept():
    assert parse_deviation('4, records "null", NO, does not record "null"') == [
        "4", 'records "null"', "NO", 'does not record "null"']


def test_longer_guidewords():
    assert parse_deviation("1, a, MORE OF, b")[2] == "MORE OF"
    assert parse_deviation("1, a, AS WELL AS, b")[2] == "AS WELL AS"


@pytest.mark.parametrize("line", ["Here are the rules:", "```csv", "1, a, b, c", "1, a, REVERSE", "1, a, REVERSE, "])
def test_unusable_lines(line):
    assert parse_deviation(line) is None


def test_trailing_comma_is_dropped():
    assert parse_deviation('"1, a, NO, not a",') == ["1", "a", "NO", "not a"]


def test_long_unusable_line_is_parsed_quickly():
    start = time.perf_counter()
    assert parse_deviation("9\ta," + " ," * 50_000) is None
    assert time.perf_counter() - start < 1


class FakeModel:
    def make_request(self, messages):
        return "Rules:\n\n1. a, b, LESS, c, d\n2. e, NO, f\n"


def test_rules_reach_the_code_generator_whole(tmp_path, capsys):
    (tmp_path / "hazop-descriptions.txt").write_text("1. a, b\n2. e\n")
    mutate_descriptions(FakeModel(), tmp_path, "prompt")
    assert read_hazop_mutations(tmp_path / "hazop-mutated-descriptions.txt") == (["c, d", "f"], 2)
    assert capsys.readouterr().out == "Unexpected format: Rules:\n"
    assert "Rules:" in (tmp_path / "hazop-mutated-descriptions-raw.txt").read_text()
