# Architecture

*multiplex* is a modular framework for prototyping LLM-based mutation testing.
One run mutates **one Java method** in a target project and evaluates the
generated mutants against that project's test suite.

## Pipeline

Orchestrated top-to-bottom by `multiplex/__main__.py`:

```
config.yml
   │
   ▼
1. Load YAML config; read all 9 system_prompts keys into a dict
   │
   ▼
2. Back up target source file to <filename>.orig
   Delete and recreate <projectroot>/output/          ← destroys previous results
   │
   ▼
3. util/extract_method.py (tree-sitter)
   Find method by name + start line
   → writes output/original_method.java
   → returns (start_byte, end_byte) offsets into the source file
   │
   ▼
4. approach/<name>/controller.main(model, output_path, prompts)
   One or more LLM calls (via model.Model / LiteLLM)
   → writes mutant files to output/<approach>-mutants/mutant_N.java
   │
   ▼
5. execute/{maven,defects4j}.run_mutants(...)
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
`main(model, output_dir, prompts)`. Dispatch is an if/elif chain in
`__main__.py` keyed on `mutation.approach`.

| Approach | Strategy | LLM calls |
|----------|----------|-----------|
| `basic` | Single system prompt, ask for a mutant 10 times | 10 |
| `hazop` | Chain: describe method line-by-line → mutate descriptions using HAZOP guidewords (NO/MORE/LESS/...) → implement each deviation | 2 + 1 per deviation |
| `stpa` | Chain: describe control flow as GraphViz DOT → identify Unsafe Control Actions (UCAs) → implement each UCA | 2 + 1 per UCA |
| `mutahunter` | Single call with AST + line-numbered source; LLM returns YAML of line-level mutations spliced in locally (prompts not bundled — licensing) | 1 |
| `llmorpheus` | tree-sitter query finds mutation sites (conditions, loop headers, call args), each replaced by `<PLACEHOLDER>`; LLM proposes 3 replacements per site | 1 per placeholder |

Intermediate artifacts are files in `output/` — approaches communicate between
their own steps via files, not in-memory state (see artifact table below).

## Execution backends (`multiplex/execute/`)

Selected by `project.runtool`:

- `d4j` → `defects4j.py` — the complete backend. Baselines the unmutated
  project first (aborts if its tests fail), times the baseline run, then runs
  each compilable mutant's tests with a timeout of 5× baseline. A surviving
  mutant is one whose test run reports `Failing tests: 0`. Requires the
  `defects4j` CLI and a `JDK_11` env var (see DEVELOPMENT.md).
- `mvn` → `maven.py` — **currently broken/incomplete**; do not rely on it
  (details in DEVELOPMENT.md § Known issues).

## Output artifacts

Everything lands under `<projectroot>/output/` (wiped at the start of each run):

| Artifact | Written by |
|----------|-----------|
| `original_method.java` | extract_method (step 3); read by every approach |
| `hazop-descriptions.txt`, `hazop-mutated-descriptions.txt` | hazop chain steps |
| `control_diagram.txt`, `ucas.csv` | stpa chain steps |
| `placeholders/{N_placeholder.java, N_orig.java, placeholders.json}` | llmorpheus site finder |
| `<approach>-mutants/mutant_N.java` | every approach's final step |
| `<approach>-mutants/mutant_summary.csv` | defects4j backend; columns `MUTANT, EQUIVALENCE, COMPILABLE, SURVIVES` |
| `<approach>-test/<mutant>_test.txt` | defects4j backend; per-mutant test output |

## LLM access (`multiplex/model.py`)

All LLM traffic goes through `Model.make_request(messages)`, a thin wrapper
over LiteLLM `completion()`. Model/endpoint come from config; the API key is
read from the environment variable *named* by `llm.token_env_var` (never stored
in config). Azure endpoints get `AZURE_AI_API_BASE`/`AZURE_AI_API_KEY` set
specially. To support another provider, replace or extend `model.py`.

LLM responses are treated as fenced code: approaches strip a leading
```` ```java ```` fence and keep everything before the next ```` ``` ```` fence.
