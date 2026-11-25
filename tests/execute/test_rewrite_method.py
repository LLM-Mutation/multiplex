"""Generated Python methods must fit back into their class."""

import ast

import pytest

from languages import get_language
from util.rewrite_method import rewrite_method

PYTHON = get_language("python")
JAVA = get_language("java")
CLASS = "class A:\n    def f(self):\n        return 1\n\n    def g(self):\n        return 2\n"
METHOD = "def f(self):\n        return 1"


def rewrite(tmp_path, reply, language=PYTHON, code=CLASS, method=METHOD):
    path = tmp_path / "a.py"
    path.with_name("a.py.orig").write_text(code)
    mutant = tmp_path / "mutant_0.py"
    mutant.write_text(reply)
    start = code.index(method)
    rewrite_method(str(path), start, start + len(method), mutant, language)
    return path.read_text()


@pytest.mark.parametrize("reply", [
    "def f(self):\n    return 3\n",
    "\ndef f(self):\n  return 3\n",
    "# DEFECT: wrong value\ndef f(self):\n    return 3\n",
    "# DEFECT: wrong value\ndef f(self):\n        return 3\n",
    "@staticmethod\ndef f(self):\n    return 3\n",
    "def f(\n    self\n):\n    return 3\n",
])
def test_reply_at_column_zero_is_indented(tmp_path, reply):
    code = rewrite(tmp_path, reply)
    assert [n.name for n in ast.parse(code).body[0].body] == ["f", "g"]


@pytest.mark.parametrize("reply", [
    "def f(self):\n        return 3",
    "    def f(self):\n        return 3",
    "# DEFECT\n    def f(self):\n        return 3",
    "def f(self): return 3",
    "def f(self:\n    return 3",
    "Here is the code",
])
def test_other_replies_are_unchanged(tmp_path, reply):
    assert rewrite(tmp_path, reply) == CLASS.replace(METHOD, reply.strip())


def test_multi_line_strings_keep_their_content(tmp_path):
    code = rewrite(tmp_path, 'def f(self):\n    x = """a\nb\n"""\n    y = f"""c\n{x}\nd"""\n    return x\n')
    values = {}
    exec(code.replace("        return x", "        return x, y"), values)
    assert values["A"]().f() == ("a\nb\n", "c\na\nb\n\nd")


def test_module_level_function_is_unchanged(tmp_path):
    code = "def f():\n    return 1\n"
    assert rewrite(tmp_path, "def f():\n  return 3", code=code, method=code.strip()) == "def f():\n  return 3\n"


def test_java_is_unchanged(tmp_path):
    reply = "def f(self):\n    return 3"
    assert rewrite(tmp_path, reply, language=JAVA) == CLASS.replace(METHOD, reply)
