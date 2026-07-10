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
   def main(model, output_dir, prompts):
       ...
   ```
   - `model` is a `model.Model`; call `model.make_request(messages)` with
     OpenAI-style message dicts.
   - Read the method under test via
     `from approach.util import get_method_under_test`.
   - Pass intermediate results between steps as files in `output_dir`
     (convention: prefix them with your approach name).
   - **Required output**: write final mutants to
     `Path(output_dir, "<name>-mutants/") / f"mutant_{count}.java"`. Each file
     must contain the complete replacement method body (it is spliced verbatim
     over the original method's byte range). Strip LLM code fences:
     ```python
     mutant = mutant.removeprefix("```java")
     mutant = mutant.split("```", 1)[0]
     ```
2. **Register the prompt key(s)**: add `<name>_...` entries to the `prompts`
   dict in `multiplex/__main__.py` *and* to the `system_prompts` section of
   every config file (including `examples/config.yml`). All keys in that dict
   are read unconditionally — omitting one breaks **every** run with KeyError,
   not just runs of your approach.
3. **Register the dispatch branch**: add an `elif config['mutation']['approach']
   == "<name>":` branch in `multiplex/__main__.py` calling
   `<name>.main(model, output_path, prompts)`, plus the corresponding
   `import approach.<name>.controller as <name>`.
4. The `-mutants` directory name must equal the `mutation.approach` config
   value — the execution backends reconstruct the path as
   `output/<approach>-mutants/`.

## Add an execution/evaluation backend

Model on `multiplex/execute/defects4j.py` (not `maven.py`, which is broken).

1. Create `multiplex/execute/<name>.py` exposing:
   ```python
   def run_mutants(project_root, original_file, output_path,
                   method_start_byte, method_end_byte, duplicate, approach):
   ```
2. The expected loop, per mutant file in `output/<approach>-mutants/`:
   - restore the pristine source: `shutil.copy2(duplicate, original_file)`
     (guard on `duplicate.exists()`);
   - `rewrite_method(original_file, method_start_byte, method_end_byte,
     mutant_path)` — note: **4 arguments**;
   - `check_mutant_equivalent(mutant_path, output/original_method.java)` and
     `check_mutant_compilable(original_file)` from `checks/`;
   - if compilable, run the project's tests with your build tool and decide
     survived/killed;
   - collect rows and finish with `write_mutant_summary(mutants_dir, rows)`
     (header row: `["MUTANT", "EQUIVALENCE", "COMPILABLE", "SURVIVES"]`).
3. Register it in `multiplex/__main__.py` under a new `project.runtool` value.
4. Useful pattern from defects4j: run the unmutated project first as a
   baseline (abort if it fails), and use a multiple of its wall-clock time as
   the per-mutant test timeout to catch infinite-loop mutants.

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
