"""Check if mutants are syntactically equivalent to original code"""
from difflib import SequenceMatcher
from tree_sitter import Parser


def _get_clean_tree(root_node, comment_node_types) -> str:
    """Serialize a parse tree to a string for comparison.

    Comments and whitespace are ignored.
    Leaf tokens include their source text to include values in comparison.
    """

    def traverse(node) -> str:
        if node.type in comment_node_types or node.type == "whitespace":
            return ""
        if node.child_count == 0:
            return node.type + "-" + node.text.decode("utf-8")
        return node.type + "(" + "".join(traverse(child) for child in node.children) + ")"

    return traverse(root_node)


def _tree_is_equivalent(original_root_node, mutant_root_node, comment_node_types):
    """Check tree for equivalence."""
    mutant = _get_clean_tree(mutant_root_node, comment_node_types)
    original = _get_clean_tree(original_root_node, comment_node_types)

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


def check_mutant_equivalent(mutant_filename, original_filename, language) -> bool:
    """Check if mutant file tree is equal to original tree.

    ``language`` is a ``languages.LanguageSpec`` selecting the tree-sitter
    grammar and which node types count as comments (ignored in the comparison).
    """
    parser = Parser(language.ts_language)
    mutant_tree = parser.parse(_read_file(mutant_filename), encoding="utf-8")
    original_tree = parser.parse(_read_file(original_filename), encoding="utf-8")
    return _tree_is_equivalent(
        original_tree.root_node, mutant_tree.root_node, language.comment_node_types
    )
