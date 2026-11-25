"""Restore the indentation of a Python function that was generated at column 0."""

import ast
import io
import tokenize


def _string_lines(text):
    """Lines that start inside a multi-line string, whose content must not change."""
    lines, starts = set(), []
    for token in tokenize.generate_tokens(io.StringIO(text).readline):
        name = tokenize.tok_name[token.type]
        if name == "STRING":
            lines.update(range(token.start[0] + 1, token.end[0] + 1))
        elif name in ("FSTRING_START", "TSTRING_START"):
            starts.append(token.start[0])
        elif name in ("FSTRING_END", "TSTRING_END"):
            lines.update(range(starts.pop() + 1, token.end[0] + 1))
    return lines


def reindent(original_code, start, text):
    """Indent ``text`` for a Python function that starts at index ``start`` of ``original_code``.

    Only text that would break the file is changed: it must be valid at column 0, and
    its body must not already be deeper than the original function. Anything else,
    including text that is not valid Python, is returned as it was.
    """
    prefix = original_code[original_code.rfind("\n", 0, start) + 1:start]
    if not prefix or prefix.strip():
        return text

    text = text.strip()
    try:
        tree = ast.parse(text)
        keep = _string_lines(text)
    except (SyntaxError, ValueError, tokenize.TokenError):
        return text

    functions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]
    if not functions:
        return text
    starts_first = len(tree.body) == 1 and functions[0].lineno == 1
    bodies = [s.col_offset for s in functions[0].body if s.lineno > functions[0].lineno]
    if starts_first and (not bodies or bodies[0] > len(prefix)):
        return text

    lines = text.split("\n")
    return "\n".join(
        prefix + line if number > 1 and number not in keep and line.strip() else line
        for number, line in enumerate(lines, 1)
    )
