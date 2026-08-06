"""The `basic` approach must honor the run's language.

`basic` is the single-prompt template every other approach follows, so these
lock in the language-aware behavior shared across all five: the mutant file
extension, the code-fence that gets stripped, and the prompt noun. The LLM is a
stub (no network) — the docs' "keep pure logic separate from make_request"
convention makes this testable.
"""

from approach.basic.code_generator import generate_code
from languages import get_language

PYTHON = get_language("python")
JAVA = get_language("java")


class FakeModel:
    """Records the messages it is handed and returns a fixed fenced response."""

    def __init__(self, response):
        self.response = response
        self.calls = []

    def make_request(self, messages):
        self.calls.append(messages)
        return self.response


def _seed_method(tmp_path, language, source):
    language.original_method_path(tmp_path).write_text(source)


def test_python_run_writes_py_mutants_and_strips_python_fence(tmp_path):
    _seed_method(tmp_path, PYTHON, "def f(n):\n    return n\n")
    model = FakeModel("```python\ndef f(n):\n    return n + 1\n```")

    generate_code(model, tmp_path, "SYSTEM", PYTHON)

    mutants = sorted((tmp_path / "basic-mutants").glob("*"))
    assert len(mutants) == 10  # basic asks 10 times
    assert all(m.suffix == ".py" for m in mutants)
    # the ```python opening fence and closing ``` are both removed
    body = mutants[0].read_text()
    assert "```" not in body
    assert body.strip() == "def f(n):\n    return n + 1"


def test_java_run_writes_java_mutants_and_strips_java_fence(tmp_path):
    _seed_method(tmp_path, JAVA, "int f(int n){ return n; }")
    model = FakeModel("```java\nint f(int n){ return n + 1; }\n```")

    generate_code(model, tmp_path, "SYSTEM", JAVA)

    mutants = sorted((tmp_path / "basic-mutants").glob("*"))
    assert mutants  # non-empty
    assert all(m.suffix == ".java" for m in mutants)
    body = mutants[0].read_text()
    assert "```" not in body
    assert body.strip() == "int f(int n){ return n + 1; }"


def test_system_prompt_uses_language_noun(tmp_path):
    _seed_method(tmp_path, PYTHON, "def f(n):\n    return n\n")
    model = FakeModel("```python\ndef f(n):\n    return n\n```")

    generate_code(model, tmp_path, "BASE PROMPT", PYTHON)

    system_content = model.calls[0][0]["content"]
    assert "Python function" in system_content  # language.noun
    assert "Java" not in system_content
