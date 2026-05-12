from multiplex.util.parser import add_mutant_to_method, parse_output


def test_add_mutant_to_method_inserts_mutant_correctly():
    numbered_src = "1: def foo():\n2:     x = 1\n3:     return x"
    mutant = "    x = 42"
    line_number = 2
    expected = "def foo():\n    x = 42\n    return x"
    result = add_mutant_to_method(numbered_src, mutant, line_number)
    assert result == expected


def test_add_mutant_to_method_preserves_indentation():
    numbered_src = "1: def bar():\n2:         y = 2\n3:         return y"
    mutant = "        y = 99"
    line_number = 2
    expected = "def bar():\n        y = 99\n        return y"
    result = add_mutant_to_method(numbered_src, mutant, line_number)
    assert result == expected


def test_add_mutant_to_method_mutant_with_less_indentation():
    numbered_src = "1: def qux():\n2:     a = 4\n3:     return a"
    mutant = "a = 0"
    line_number = 2
    expected = "def qux():\n    a = 0\n    return a"
    result = add_mutant_to_method(numbered_src, mutant, line_number)
    assert result == expected


def test_add_mutant_to_method_line_number_out_of_range():
    numbered_src = "1: def foo():\n2:     x = 1"
    mutant = "    x = 42"
    line_number = 5
    expected = "def foo():\n    x = 1"
    result = add_mutant_to_method(numbered_src, mutant, line_number)
    assert result == expected

def test_parse_output_valid_yaml():
    input_str = "```yaml\nfoo: bar\nbaz: 1\n```"
    expected = {"foo": "bar", "baz": 1}
    result = parse_output(input_str)
    assert result == expected

def test_parse_output_invalid_yaml():
    input_str = "```yaml\nfoo: [unclosed_list\n```"
    result = parse_output(input_str)
    assert result is None

def test_parse_output_no_yaml_prefix_suffix():
    input_str = "foo: bar\nbaz: 2"
    expected = {"foo": "bar", "baz": 2}
    result = parse_output(input_str)
    assert result == expected

def test_parse_output_empty_string():
    input_str = ""
    result = parse_output(input_str)
    assert result is None or result == {}

def test_parse_output_non_yaml_content():
    input_str = "```yaml\nnot: yaml: content\n```"
    result = parse_output(input_str)
    assert result is None

