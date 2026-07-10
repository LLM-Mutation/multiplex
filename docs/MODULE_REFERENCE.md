# Module Reference

Function-level reference for every module. Paths are relative to `multiplex/`.
Signatures are exact; use this instead of opening source files.

Note on imports: inside `multiplex/` modules import each other without the
package prefix (e.g. `from util.io import write_to_file`). See DEVELOPMENT.md.

## model.py

```python
class Model:
    def __init__(self, model=None, endpoint=None, api_key_var=None)
    def current_model(self) -> str
    def make_request(self, messages) -> str   # returns response.choices[0].message.content
```

- `api_key_var` is the **name** of an env var; its value is read from
  `os.environ` (KeyError if the named var is unset).
- If `"azure" in endpoint`, sets `AZURE_AI_API_BASE` and `AZURE_AI_API_KEY`.
- `messages` is a LiteLLM/OpenAI-style list of `{"role": ..., "content": ...}`.

## prompts.py

```python
APPROACH_PROMPT_KEYS: dict[str, list[str]]     # approach name -> required system_prompts keys
resolve_prompts(config, approach) -> dict      # {key: prompt} for the approach's keys
```

- `resolve_prompts` reads only the selected approach's keys from
  `config["system_prompts"]`. Raises `SystemExit` (actionable message) if
  `approach` is unknown or any required key is missing/empty. Pure function, no
  I/O — called by `__main__.py` before any destructive step. Importable in tests
  as `from multiplex.prompts import ...` (no sibling imports, so it works under
  both the flat runtime import and the package-prefixed test import).

## util/io.py

```python
write_to_file(output_file_path, output)            # plain text write (mode "w")
write_ucas(ucas_output_path, ucas_output)          # writes str line-by-line
write_mutant_summary(mutants_dir, mutants)         # writes mutants_dir/mutant_summary.csv from list-of-rows
read_input_to_str(input_file_path) -> str
read_ucas(input_file_path) -> (list[str], int)     # (lines, line count)
read_hazop_mutations(input_file_path) -> (list[str], int)  # 4th CSV column of each line
reset_source_code(duplicate_file_path, filename)
```

- `reset_source_code`: if `<filename>.orig` exists, moves it over `filename`
  (restore); then always re-copies `filename` → `.orig`. Called at run start
  and end by `__main__.py`.

## util/extract_method.py

```python
extract_method_from_file(file_path, method_name, output_dir, start_line)
    -> (start_byte, end_byte) | None
```

- tree-sitter walk for a `method_declaration`/`constructor_declaration` whose
  identifier text == `method_name` **and** whose identifier is on line
  `start_line` (1-based). Both must match — `start_line` is the line of the
  method *name*, not of annotations above it.
- Writes the method source to `output_dir/original_method.java`.
- Returns `None` if not found (logs a warning). Caller in `__main__.py`
  unpacks the tuple directly, so a miss crashes with TypeError.

## util/rewrite_method.py

```python
rewrite_method(orig_path, start_byte, end_byte, mutant_file_path)
```

- Reads the pristine file from `orig_path + ".orig"` (the backup), splices the
  mutant file's stripped text over bytes `[start_byte:end_byte)`, writes the
  result to `orig_path`. Byte offsets come from `extract_method_from_file`.

## util/parser.py

```python
parse_output(input) -> dict | None      # strips ```yaml fences, yaml.safe_load; None on parse error
add_mutant_to_method(numbered_src, mutant, line_number) -> str
```

- `add_mutant_to_method` takes source whose lines are prefixed `"N: "`,
  replaces line `line_number` with `mutant` (preserving indentation), and
  returns un-numbered source. Used by the mutahunter approach.

## checks/compilable.py

```python
check_mutant_compilable(filename) -> bool
```

- **Not a real compile.** tree-sitter parses the file and returns False if any
  `ERROR` or missing node exists. Catches syntax errors only — type errors,
  missing symbols, etc. pass.

## checks/syntactic_equivalence.py

```python
check_mutant_equivalent(mutant_filename, original_filename) -> bool
```

- Serializes both files' tree-sitter ASTs to strings, dropping comment nodes;
  True iff the strings are identical. Detects mutants that only change
  comments/formatting. Prints a `SequenceMatcher` similarity ratio as a side
  effect (not used in the decision).

## approach/util.py

```python
get_method_under_test(output_dir) -> str   # reads output_dir/original_method.java; FileNotFoundError if absent
```

## approach/*/controller.py (all five)

```python
main(model, output_dir, prompts)   # prompts: the full dict built in __main__.py
```

Each controller just calls its package's step functions in order with the
relevant `prompts[...]` key(s):

- `basic`: `code_generator.generate_code` — 10 requests, each response saved as
  `basic-mutants/mutant_N.java`.
- `hazop`: `method_explainer.describe_method` → `hazop-descriptions.txt`;
  `description_mutator.mutate_descriptions` → `hazop-mutated-descriptions.txt`
  (CSV rows `number, original_rule, GUIDEWORD, changed_rule`);
  `code_generator.generate_code` → one mutant per changed rule.
- `stpa`: `control_diagram.create_control_diagram` → `control_diagram.txt` (DOT);
  `uca_generator.generate_ucas` → `ucas.csv`;
  `code_generator.generate_code` → one mutant per UCA
  (loop is `range(0, ucas_count - 1)`: the **last UCA is skipped** — see
  DEVELOPMENT.md § Known issues).
- `mutahunter`: `code_generator.generate_code` — one request containing the
  method's AST plus line-numbered source; expects YAML back with
  `mutants: [{mutated_code, line_number}, ...]`, spliced locally via
  `util.parser.add_mutant_to_method`. The user-prompt template is intentionally
  gutted (licensing) — users must fill in Mutahunter's own prompt text.
- `llmorpheus`: `placeholders.create_placeholders` — tree-sitter query captures
  if/while/do/switch conditions, for-loop parts, enhanced-for parts, loop
  headers, and method-call names/receivers/args; each capture produces
  `placeholders/N_placeholder.java` (method with `<PLACEHOLDER>` substituted),
  `placeholders/N_orig.java` (original fragment), and an entry in
  `placeholders/placeholders.json` (`{tag, start_byte, end_byte, text}`).
  `code_generator.generate_code` — one request per placeholder asking for 3
  replacements ("Option 1/2/3" fenced blocks, extracted with the regex
  ```` \n```\n(.*?)\n``` ```` under `re.DOTALL`); each replacement spliced into
  the method at the placeholder's byte offsets →
  `llmorpheus-mutants/mutant_N.java`.

## execute/defects4j.py

```python
run_mutants(project_root, original_file, output_path,
            method_start_byte, method_end_byte, duplicate, approach)
```

- `_execute(project_root, file=None, approach=None, timer=None) -> bool`:
  deletes `.classes_instrumented`/`target`, runs `defects4j test -w
  <project_root>` with `PATH += ./defects4j/framework/bin` and
  `JAVA_HOME = $JDK_11`; True iff output contains `Failing tests: 0`.
  With `timer` set it enforces a subprocess timeout and writes test output to
  `output/<approach>-test/<mutant>_test.txt`. Kills stray Java processes after.
- `run_mutants` baselines the original project (raises IOError if its tests
  fail), sets per-mutant timeout = 5× baseline duration, then per mutant:
  restore from backup → equivalence check → rewrite → compilable check →
  (if compilable) run tests. Appends `[name, equivalent, compilable, survives]`
  rows and writes `mutant_summary.csv`.

## execute/maven.py

```python
run_mutants(project_root, filename, output_path,
            method_start_byte, method_end_byte, duplicate, approach)
```

- `_execute(project_root) -> bool`: runs `mvn -f <project_root> clean test`;
  True if the output contains `BUILD SUCCESS` (all tests green → mutant
  survived), False otherwise (mutant killed, incl. compile failures Maven
  catches that tree-sitter does not).
- `run_mutants`: same flow as the Defects4J backend — baseline the original
  project (raises `IOError` if its tests fail), then per mutant: restore from
  backup → equivalence check → rewrite → compilable check → (if compilable) run
  tests → append `[name, equivalent, compilable, survives]` → write
  `mutant_summary.csv`. Drives the runnable example under `examples/`.
