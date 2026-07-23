"""Per-language facts for the mutation pipeline.

A ``LanguageSpec`` carries everything the language-agnostic pipeline needs to
work with a given source language: the tree-sitter grammar, the node types that
denote a mutable definition, which nodes count as comments (ignored by the
syntactic-equivalence check), the code-fence tag and prompt wording the
approaches use, and the on-disk extension for the method/mutant artifacts.

Adding a language means adding one ``LanguageSpec`` to ``_REGISTRY`` (plus a
prompt set and an example) — see docs/EXTENDING.md § Add a language.
"""

from dataclasses import dataclass
from pathlib import Path

from tree_sitter import Language
import tree_sitter_java as ts_java
import tree_sitter_python as ts_python

# Base name (without extension) of the method-under-test artifact every approach
# reads from the output directory.
_METHOD_STEM = "original_method"


@dataclass(frozen=True)
class LanguageSpec:
    """Everything the pipeline needs to know about one source language."""

    name: str
    extension: str
    ts_language: Language
    def_node_types: frozenset
    comment_node_types: frozenset
    fence: str
    noun: str
    label: str

    def original_method_path(self, output_dir) -> Path:
        """Path of the extracted method-under-test artifact for this language."""
        return Path(output_dir, _METHOD_STEM + self.extension)


_REGISTRY = {
    "java": LanguageSpec(
        name="java",
        extension=".java",
        ts_language=Language(ts_java.language()),
        def_node_types=frozenset({"method_declaration", "constructor_declaration"}),
        comment_node_types=frozenset({"comment", "line_comment", "block_comment"}),
        fence="java",
        noun="Java method",
        label="Java",
    ),
    "python": LanguageSpec(
        name="python",
        extension=".py",
        ts_language=Language(ts_python.language()),
        def_node_types=frozenset({"function_definition"}),
        comment_node_types=frozenset({"comment"}),
        fence="python",
        noun="Python function",
        label="Python",
    ),
}

DEFAULT_LANGUAGE = "java"


def get_language(name=None) -> LanguageSpec:
    """Return the ``LanguageSpec`` for ``name`` (defaults to Java).

    Raises ``SystemExit`` with an actionable message if ``name`` is unknown, so
    a bad ``project.language`` fails fast before any destructive step — mirroring
    ``prompts.resolve_prompts``.
    """
    key = (name or DEFAULT_LANGUAGE).lower()
    if key not in _REGISTRY:
        valid = ", ".join(sorted(_REGISTRY))
        raise SystemExit(f"Invalid language '{name}'. Choose one of: {valid}")
    return _REGISTRY[key]
