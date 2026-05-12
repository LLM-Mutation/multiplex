from tree_sitter import Language, Node, Parser
import tree_sitter_java as ts_java


def tree_has_for_errors(node: Node):
    """Check Tree for Compilation Errors."""
    errors_present = False
    for n in node.children:
        if n.type == "ERROR" or n.is_missing:
            return True
        errors_present = tree_has_for_errors(n)
    return errors_present


def _read_file(fn):
    src = ""
    with open(fn, "r", encoding="utf-8") as reader:
        src = reader.read()
    return bytes(src.encode("utf-8"))


def check_mutant_compilable(filename):
    """Check if Java file contains compilation errors"""
    language = Language(ts_java.language())
    parser = Parser(language)
    tree = parser.parse(_read_file(filename), encoding="utf8")

    return not tree_has_for_errors(tree.root_node)
