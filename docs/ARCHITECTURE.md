# Architecture

*multiplex* is a modular framework for prototyping LLM-based mutation testing.
One run mutates **one method/function** in a target project and evaluates the
generated mutants against that project's test suite. The source language is set
by `project.language` (`java` — the default — or `python`); see the language
registry below.

## Pipeline

Orchestrated top-to-bottom by `multiplex/__main__.py`:

```
config.yml
   │
   ▼
1. Load YAML config; resolve the approach's system_prompts and the language
   (languages.get_language(project.language), default "java")
   │
   ▼
2. Back up target source file to <filename>.orig
   Delete and recreate <projectroot>/output/          ← destroys previous results
   │
   ▼
3. util/extract_method.py (tree-sitter, grammar from the LanguageSpec)
   Find method/function by name + start line
   → writes output/original_method.<ext>   (.java / .py)
   → returns (start_byte, end_byte) offsets into the source file
   │
   ▼
4. approach/<name>/controller.main(model, output_path, prompts, language)
   One or more LLM calls (via model.Model / LiteLLM)
   → writes mutant files to output/<approach>-mutants/mutant_N.<ext>
   │
   ▼
5. execute/{maven,defects4j,pytest_runner}.run_mutants(...)
   For each mutant file:
     a. restore source file from .orig backup
     b. util/rewrite_method.py splices mutant text into the file
        at the saved byte offsets
     c. checks/compilable.py        — tree-sitter parse-error scan
        checks/syntactic_equivalence.py — AST equality vs original (ignores comments)
     d. run the project's tests (Defects4J backend only; see Status below)
   → writes output/<approach>-mutants/mutant_summary.csv (Defects4J)
   │
   ▼
6. Restore original source file from .orig backup
```

Key mechanism: the method's **byte offsets** captured in step 3 are reused in
step 5b to splice each mutant into a pristine copy of the file. Anything that
changes the file between those steps invalidates the offsets.

## Mutant-generation approaches (`multiplex/approach/`)

Each approach is a package with a `controller.py` exposing
`main(model, output_dir, prompts, language)`. Dispatch is an if/elif chain in
`__main__.py` keyed on `mutation.approach`.

| Approach | Strategy | LLM calls |
|----------|----------|-----------|
| `basic` | Single system prompt, ask for a mutant 10 times | 10 |
| `hazop` | Chain: describe method line-by-line → mutate descriptions using HAZOP guidewords (NO/MORE/LESS/...) → implement each deviation | 2 + 1 per deviation |
| `stpa` | Chain: describe control flow as GraphViz DOT → identify Unsafe Control Actions (UCAs) → implement each UCA | 2 + 1 per UCA |
| `mutahunter` | Single call with AST + line-numbered source; LLM returns YAML of line-level mutations spliced in locally (prompts not bundled — licensing) | 1 |
| `llmorpheus` | tree-sitter query finds mutation sites (conditions, loop headers, call args), each replaced by `<PLACEHOLDER>`; LLM proposes 3 replacements per site | 1 per placeholder |

All five approaches are language-aware via the `language` argument (file
extension, code fence, prompt noun). llmorpheus additionally selects its
mutation-site query per language from `MUTATION_QUERIES` in
`approach/llmorpheus/placeholders.py`.

Intermediate artifacts are files in `output/` — approaches communicate between
their own steps via files, not in-memory state (see artifact table below).

## Execution backends (`multiplex/execute/`)

Selected by `project.runtool`:

- `d4j` → `defects4j.py` — the complete backend. Baselines the unmutated
  project first (aborts if its tests fail), times the baseline run, then runs
  each compilable mutant's tests with a timeout of 5× baseline. A surviving
  mutant is one whose test run reports `Failing tests: 0`. Requires the
  `defects4j` CLI and a `JDK_11` env var (see DEVELOPMENT.md).
- `mvn` → `maven.py` — self-contained backend for plain Maven projects. Runs
  `mvn -f <project_root> clean test`; a mutant survives if the build passes
  (`BUILD SUCCESS`). Baselines the original first (aborts if its tests fail),
  then per mutant does the same equivalence → rewrite → compilable → test →
  summary flow as the Defects4J backend. Used by the runnable Java example under
  `examples/` (see DEVELOPMENT.md § Example).
- `pytest` → `pytest_runner.py` — self-contained backend for Python projects.
  Runs `sys.executable -m pytest -q <project_root>` (pytest under multiplex's own
  interpreter); a mutant survives if pytest exits 0 (all tests pass). Same
  baseline → per-mutant flow as the Maven backend. Drives the runnable Python
  example (`examples/config-python.yml`). Named `pytest_runner` so it does not
  shadow the installed `pytest` package.

## Language registry (`multiplex/languages/`)

`get_language(project.language)` returns a `LanguageSpec` (grammar, definition
node types, comment node types, extension, code-fence tag, prompt noun,
mutahunter label). It is resolved once in `__main__.py` and threaded into
`extract_method`, every approach's `main`, the checks, and the execution
backend — so the pipeline is language-agnostic and adding a language is a
registry entry plus prompts and an example (see docs/EXTENDING.md § Add a
language). `project.language` defaults to `java`.

## Output artifacts

Everything lands under `<projectroot>/output/` (wiped at the start of each run):

| Artifact | Written by |
|----------|-----------|
| `original_method.<ext>` | extract_method (step 3); read by every approach (`.java`/`.py`) |
| `hazop-descriptions.txt`, `hazop-mutated-descriptions.txt` | hazop chain steps |
| `control_diagram.txt`, `ucas.csv` | stpa chain steps |
| `placeholders/{N_placeholder.<ext>, N_orig.<ext>, placeholders.json}` | llmorpheus site finder |
| `<approach>-mutants/mutant_N.<ext>` | every approach's final step |
| `<approach>-mutants/mutant_summary.csv` | maven/defects4j/pytest backends; columns `MUTANT, EQUIVALENCE, COMPILABLE, SURVIVES` |
| `<approach>-test/<mutant>_test.txt` | defects4j backend; per-mutant test output |

## LLM access (`multiplex/model.py`)

All LLM traffic goes through `Model.make_request(messages)`, a thin wrapper
over LiteLLM `completion()`. Model/endpoint come from config; the API key is
read from the environment variable *named* by `llm.token_env_var` (never stored
in config). Azure endpoints get `AZURE_AI_API_BASE`/`AZURE_AI_API_KEY` set
specially. To support another provider, replace or extend `model.py`.

LLM responses are treated as fenced code: approaches strip a leading
```` ```<lang> ```` fence (the tag is `language.fence`, e.g. `java`/`python`) and
keep everything before the next ```` ``` ```` fence.
