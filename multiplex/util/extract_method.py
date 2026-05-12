import logging
from pathlib import Path
import tree_sitter_java as ts_java
from tree_sitter import Language, Parser

JAVA_LANGUAGE = Language(ts_java.language())
OUTPUT_FILE = "original_method.java"


def extract_method_from_file(file_path, method_name, output_dir, start_line):
    """Extract method from source code."""
    output_file = Path(output_dir, OUTPUT_FILE)

    parser = Parser(JAVA_LANGUAGE)

    with open(file_path, "r") as f:
        code = f.read()
    code_bytes = code.encode()

    tree = parser.parse(code_bytes)
    root_node = tree.root_node

    def find_method(node):

        if node.type == "method_declaration" or node.type == "constructor_declaration":
            for child in node.children:
                if (
                    child.type == "identifier"
                    and code_bytes[child.start_byte : child.end_byte].decode()
                    == method_name
                    and child.start_point.row + 1 == int(start_line)
                ):
                    return node
        for child in node.children:
            result = find_method(child)
            if result:
                return result
        return None

    method_node = find_method(root_node)
    if method_node:
        method_source = code_bytes[
            method_node.start_byte : method_node.end_byte
        ].decode()
        print("=== Method Found ===\n")
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(method_source)
        return method_node.start_byte, method_node.end_byte

    logging.warning("Method '%s' not found in file '%s'.", method_name, file_path)
    return None
