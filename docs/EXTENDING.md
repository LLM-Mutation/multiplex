# Extending multiplex

Checklists for adding modules. Follow the import convention: inside
`multiplex/`, import siblings **without** the `multiplex.` prefix
(DEVELOPMENT.md § Import convention).

## Add a mutant-generation approach

Use `approach/basic/` as the single-prompt template or `approach/hazop/` as
the multi-prompt-chain template.

1. **Create the package** `multiplex/approach/<name>/` with `__init__.py` and
   `controller.py` exposing:
   ```python
   def main(model, output_dir, prompts, language):
       ...
   ```
   - `model` is a `model.Model`; call `model.make_request(messages)` with
     OpenAI-style message dicts.
   - `language` is a `languages.LanguageSpec` (resolved in `__main__.py`); use it
     for anything language-specific — `language.extension`, `language.fence`,
     `language.noun` — so your approach works for every registered language.
   - Read the method under test via
     `from approach.util import get_method_under_test` — call it as
     `get_method_under_test(output_dir, language)`.
   - Pass intermediate results between steps as files in `output_dir`
     (convention: prefix them with your approach name).
   - **Required output**: write final mutants to
     `Path(output_dir, "<name>-mutants/") / f"mutant_{count}{language.extension}"`.
     Each file must contain the complete replacement method body (it is spliced
     verbatim over the original method's byte range). Strip LLM code fences:
     ```python
     mutant = mutant.removeprefix("```" + language.fence)
     mutant = mutant.split("```", 1)[0]
     ```
2. **Register the prompt key(s)**: add a `"<name>": [...]` entry to
   `APPROACH_PROMPT_KEYS` in `multiplex/prompts.py` listing the
   `system_prompts` keys your approach reads. Only the selected approach's keys
   are required at runtime, so users running other approaches need not define
   yours (and vice versa). Document the keys in `docs/CONFIG.md`; adding them to
   `examples/config-java.yml` (a commented stub is fine) is optional but helpful.
3. **Register the dispatch branch**: add an `elif config['mutation']['approach']
   == "<name>":` branch in `multiplex/__main__.py` calling
   `<name>.main(model, output_path, prompts, language)`, plus the corresponding
   `import approach.<name>.controller as <name>`.
4. The `-mutants` directory name must equal the `mutation.approach` config
   value — the execution backends reconstruct the path as
   `output/<approach>-mutants/`.

## Add an execution/evaluation backend

Model on `multiplex/execute/defects4j.py` or `multiplex/execute/maven.py`
(both follow the same flow; `maven.py` is the simpler, self-contained one).

1. Create `multiplex/execute/<name>.py` exposing:
   ```python
   def run_mutants(project_root, original_file, output_path,
                   method_start_byte, method_end_byte, duplicate, approach,
                   language):
   ```
   `language` is a `languages.LanguageSpec` — use it for the artifact path and
   the checks below.
2. The expected loop, per mutant file in `output/<approach>-mutants/`:
   - restore the pristine source: `shutil.copy2(duplicate, original_file)`
     (guard on `duplicate.exists()`);
   - `rewrite_method(original_file, method_start_byte, method_end_byte,
     mutant_path)` — note: **4 arguments**;
   - `check_mutant_equivalent(mutant_path,
     language.original_method_path(output_path), language)` and
     `check_mutant_compilable(original_file, language)` from `checks/`;
   - if compilable, run the project's tests with your build tool and decide
     survived/killed;
   - collect rows and finish with `write_mutant_summary(mutants_dir, rows)`
     (header row: `["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]`).
3. Register it in `multiplex/__main__.py` under a new `project.runtool` value
   (pass `language` through to `run_mutants`).
4. Useful pattern from defects4j: run the unmutated project first as a
   baseline (abort if it fails), and use a multiple of its wall-clock time as
   the per-mutant test timeout to catch infinite-loop mutants.

## Add a language

The pipeline is language-agnostic: the parser, checks, approaches and execution
backends all take a `languages.LanguageSpec` resolved once in `__main__.py` from
the `project.language` config value. Java and Python ship in
`multiplex/languages/__init__.py`.

To add a language:

1. **Add the tree-sitter grammar** dependency (e.g. `tree-sitter-<lang>`) to
   `pyproject.toml` and add a `LanguageSpec` entry to `_REGISTRY` in
   `multiplex/languages/__init__.py`:
   ```python
   "<lang>": LanguageSpec(
       name="<lang>",
       extension=".<ext>",
       ts_language=Language(ts_<lang>.language()),
       def_node_types=frozenset({...}),      # nodes that denote a definition
       comment_node_types=frozenset({...}),  # ignored by the equivalence check
       fence="<lang>",                       # ```<lang> fence tag
       noun="<Lang> function",               # prompt wording
       label="<Lang>",                       # mutahunter language string
   ),
   ```
   `def_node_types` are the node types `extract_method` matches (their child
   `identifier` is compared to `project.method`); `comment_node_types` are
   dropped when comparing ASTs for syntactic equivalence. Inspect a grammar with
   a few lines of tree-sitter to find the right node types.
2. **Provide a prompt set** for the language in the config's `system_prompts`
   (see `examples/config-python.yml`). Prompt *keys* are shared across languages;
   only the wording differs. mutahunter prompts remain user-supplied.
3. **Add a mutation-site query for llmorpheus** if you want that approach:
   add a `"<lang>": <QUERY>` entry to `MUTATION_QUERIES` in
   `multiplex/approach/llmorpheus/placeholders.py` (keyed by `language.name`).
   The other four approaches work with no per-approach changes.
4. **Pick an execution backend**: reuse an existing `project.runtool`
   (`mvn`/`d4j`/`pytest`) or add one (see the section above). `pytest_runner.py`
   is the template for a script/test-command backend.
5. **Add an end-to-end example** under `examples/` (a small project + a config
   with `project.language: <lang>`), mirroring `examples/project/python-example/`.

Existing configs are unaffected: `project.language` defaults to `java`.

## Add / change the LLM provider

`multiplex/model.py` wraps LiteLLM, so most providers work by editing only the
config (`llm.model`, `llm.endpoint`, `llm.token_env_var`). If a provider needs
extra setup (custom env vars, headers), extend `Model.__init__` — see the
existing Azure special-case. Keep the `make_request(messages) -> str` interface
unchanged; every approach depends on it.

## Testing your module

Put tests under `tests/<area>/test_<module>.py` with fixture files in
`tests/resources/`. Import production code **with** the package prefix
(`from multiplex.checks.compilable import ...`). Run from the repo root:
`uv run pytest tests`. LLM calls are not mocked anywhere yet — keep pure logic
(parsing, splicing, checks) in functions separate from `model.make_request`
call sites so it is testable without an LLM.
