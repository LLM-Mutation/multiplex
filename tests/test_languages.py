from pathlib import Path

import pytest

from multiplex.languages import DEFAULT_LANGUAGE, get_language


def test_get_python_spec_fields():
    py = get_language("python")
    assert py.name == "python"
    assert py.extension == ".py"
    assert "function_definition" in py.def_node_types
    assert "comment" in py.comment_node_types
    assert py.fence == "python"
    assert py.label == "Python"


def test_get_java_spec_fields():
    java = get_language("java")
    assert java.name == "java"
    assert java.extension == ".java"
    assert "method_declaration" in java.def_node_types


def test_default_is_java():
    assert DEFAULT_LANGUAGE == "java"
    assert get_language(None).name == "java"
    assert get_language().name == "java"


def test_original_method_path_uses_extension():
    assert get_language("python").original_method_path("out") == Path("out/original_method.py")
    assert get_language("java").original_method_path("out") == Path("out/original_method.java")


def test_unknown_language_raises_systemexit():
    with pytest.raises(SystemExit) as exc:
        get_language("ruby")
    msg = str(exc.value)
    assert "ruby" in msg
    assert "java" in msg and "python" in msg


def test_language_name_is_case_insensitive():
    assert get_language("Python").name == "python"
    assert get_language("JAVA").name == "java"
