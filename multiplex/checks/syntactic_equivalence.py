"""Check if mutants are syntactically equivalent to original code"""
from difflib import SequenceMatcher
from tree_sitter import Language, Parser
import tree_sitter_java as ts_java


def _get_clean_tree(root_node) -> str:
    """Serialize a parse tree to a string for comparison.

    Comments and whitespace are ignored. 
    Leaf tokens include their source text to include values in comparison.
    """

    def traverse(node) -> str:
        if node.type in ("comment", "line_comment", "block_comment", "whitespace"):
            return ""
        if node.child_count == 0:
            return node.type + "-" + node.text.decode("utf-8")
        return node.type + "(" + "".join(traverse(child) for child in node.children) + ")"

    return traverse(root_node)


def _tree_is_equivalent(original_root_node, mutant_root_node):
    """Check tree for equivalence."""
    mutant = _get_clean_tree(mutant_root_node)
    original = _get_clean_tree(original_root_node)

    seq_match = SequenceMatcher(None, original, mutant)
    ratio = seq_match.ratio()
    print("Syntactic Equivalence Ratio:", ratio)

    return mutant == original


def _read_file(fn):
    """Read file"""
    src = ""
    with open(fn, "r", encoding="utf-8") as reader:
        src = reader.read()
    return bytes(src.encode("utf-8"))


def check_mutant_equivalent(mutant_filename, original_filename) -> bool:
    """Check if mutant file tree is equal to original tree."""
    language = Language(ts_java.language())
    parser = Parser(language)
    mutant_tree = parser.parse(_read_file(mutant_filename), encoding="utf-8")
    original_tree = parser.parse(_read_file(original_filename), encoding="utf-8")
    return _tree_is_equivalent(original_tree.root_node, mutant_tree.root_node)
