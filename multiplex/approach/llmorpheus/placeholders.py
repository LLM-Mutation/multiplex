from pathlib import Path
import tree_sitter_java as ts_java
from tree_sitter import Language, Node, Parser
from approach.util import get_method_under_test
import json

PLACEHOLDER = "<PLACEHOLDER>"
JAVA_LANGUAGE = Language(ts_java.language())
parser = Parser(JAVA_LANGUAGE)
JAVA_QUERY = """
; --- (i) IF, SWITCH, WHILE, DO-WHILE ---
(if_statement condition: (parenthesized_expression (_) @condition.if))
(while_statement condition: (parenthesized_expression (_) @condition.while))
(do_statement condition: (parenthesized_expression (_) @condition.do))
(switch_expression condition: (parenthesized_expression) @condition.switch)

; --- (ii) FOR LOOPS  ---
(for_statement
    init: (_)? @loop.init
    condition: (_)? @loop.condition
    update: (_)? @loop.update
)
(enhanced_for_statement
    ; Java uses 'type' and 'name' for the variable part
    type: (_) @loop.init.type
    name: (identifier) @loop.init.name
    value: (_) @loop.iterable
)

; --- (ii) LOOP HEADERS  ---
(for_statement (parenthesized_expression) @loop.header_content)
(enhanced_for_statement (parenthesized_expression) @loop.header_content)

; --- (iii) FUNCTION CALLS ---
(method_invocation
    name: (identifier) @call.name
    object: (_)? @call.receiver
    arguments: (argument_list 
        (_) @call.arg
    ) @call.arg_sequence_content
)
"""


def find_placeholder_locations(root, source_code):
    query = JAVA_LANGUAGE.query(JAVA_QUERY)
    captures: dict[str, list[Node]] = query.captures(root)

    results = []

    for tag, nodes in captures.items():
        for node in nodes:
            results.append(
                {
                    "tag": tag,
                    "start_byte": node.start_byte,
                    "end_byte": node.end_byte,
                    "text": source_code[node.start_byte : node.end_byte],
                }
            )

    return results


def add_placeholder(m, code_bytes):

    return (
        code_bytes[: m["start_byte"]]
        + PLACEHOLDER.encode()
        + code_bytes[m["end_byte"] :]
    )


def create_placeholders(output_dir: Path):
    method_under_test = get_method_under_test(output_dir)

    code_bytes = method_under_test.encode()

    tree = parser.parse(code_bytes)
    root_node = tree.root_node

    matches = find_placeholder_locations(root_node, method_under_test)

    count = 0
    placeholder_dir = Path(output_dir, "placeholders")
    placeholder_dir.mkdir(parents=True, exist_ok=True)

    locations_dict = {}
    for m in matches:
        p = add_placeholder(m, code_bytes)
        orig_p = m["text"]
        
        p_f = f"{count}_placeholder.java"
        p_fn = Path(placeholder_dir, p_f)
        locations_dict[p_f] = m

        orig_p_fn = Path(placeholder_dir, f"{count}_orig.java")

        p_fn.write_text(p if isinstance(p, str) else p.decode())
        orig_p_fn.write_text(orig_p if isinstance(orig_p, str) else orig_p.decode())

        count+=1

    placeholders_json = Path(placeholder_dir, "placeholders.json")
    with placeholders_json.open("w") as f:
        json.dump(locations_dict, f, indent=2)
