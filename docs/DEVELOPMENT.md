# Development Guide

## Setup and commands

Dependency management is [uv](https://github.com/astral-sh/uv); Python >= 3.13.

```bash
uv sync -p 3.13                  # install deps incl. dev group (pytest, ruff, pylint)
uv run pytest tests              # all tests — run from the REPO ROOT
uv run pytest tests/checks/test_compiles.py                # one file
uv run pytest tests/checks/test_compiles.py::test_name     # one test
uv run ruff check .              # lint (CI uses --output-format=github)
uv run ./multiplex ./path/to/config.yml                    # run the tool
```

- **Pin Python 3.13** (as CI does): `requires-python` allows >= 3.13, but
  litellm's `tiktoken` dependency fails to build on 3.14.
- Tests must run from the repo root: they reference `tests/resources/...`
  relatively.
- Running the tool needs a reachable LLM endpoint and a target Java project;
  `d4j` runs additionally need the `defects4j` CLI (expected under
  `./defects4j/framework/bin`) and a `JDK_11` env var pointing at a JDK 11 home.

CI (GitHub Actions, on push/PR to `main`): `test.yml` runs
`uv run pytest tests` on Python 3.13; `ruff.yml` runs `uv run ruff check`.

## Example

A self-contained end-to-end example lives under `examples/`:

```bash
uv run multiplex ./examples/config.yml     # from the repo root
```

- Target: `examples/project/example/` — a tiny Maven project with one method
  (`com.example.Classifier.classify`) and JUnit tests pinning its behavior.
- `examples/config.yml` uses the `basic` approach and the `mvn` runtool.
- Prerequisites: `mvn` + a JDK 11+ on PATH (the project targets Java 11; if
  `mvn` picks up an older JDK via `JAVA_HOME` the compile fails with "release
  version 11 not supported"), and a running Ollama serving the model
  named in `llm.model` (default `gpt-oss:20b`; point it at any model you have,
  e.g. `ollama pull gpt-oss:20b`). Any LiteLLM-supported endpoint works if you
  edit `llm`.
- Output lands in `examples/project/example/output/basic-mutants/`
  (`mutant_N.java` plus `mutant_summary.csv`). Run artifacts (`output/`,
  `*.orig`, Maven `target/`) are git-ignored.
- The `basic` approach makes 10 LLM calls and the `mvn` backend runs the test
  suite once per compilable mutant, so a full run takes a few minutes (longer
  on a slow/local model).

## Import convention (critical)

The tool is executed as a directory (`uv run ./multiplex`), which puts
`multiplex/` itself on `sys.path`:

- **Inside `multiplex/`**: flat imports, no package prefix —
  `from model import Model`, `from util.io import write_to_file`,
  `import approach.basic.controller as basic`.
- **Inside `tests/`**: package-prefixed imports —
  `from multiplex.checks.syntactic_equivalence import check_mutant_equivalent`.

Using the wrong style in either place breaks at import time. This also means
`multiplex/` modules are not importable as `multiplex.x` **and** `x` in the
same process; keep the two worlds separate.

## Conventions

- tree-sitter is the universal Java analysis tool (extraction, compilability,
  equivalence, placeholder finding). Versions are pinned
  (`tree-sitter==0.23.2`, `tree-sitter-java==0.23.5`); the code depends on that
  API — do not bump casually.
- Approaches communicate between their own steps via files in `output/`, not
  in-memory state; artifact names are prefixed with the approach name.
- LLM code responses are unfenced by stripping a leading ```` ```java ````
  fence and truncating at the next ```` ``` ```` fence
  (`removeprefix` + `split`, see EXTENDING.md for the exact two lines).
- Mutant files are named `mutant_<N>.java` in `output/<approach>-mutants/`.
- Status/progress reporting is `print()`-based throughout (no logging config,
  one `logging.warning` in extract_method).

## Known issues and gotchas (verified 2026-07)

Bugs — fix or work around, don't replicate:

1. **STPA off-by-one**: `approach/stpa/code_generator.py` loops
   `range(0, ucas_count - 1)`, silently skipping the last UCA.
2. **Method-not-found crash**: `extract_method_from_file` returns `None` on a
   miss, but `__main__.py` unpacks it as a tuple → opaque TypeError. Symptom:
   check `project.method`/`project.line` in the config (`line` must be the
   line of the method-name identifier).
3. **README key mismatch**: README shows `llm.tokenenvvar`; the code reads
   `llm.token_env_var` (the example config is correct).
4. **`tests/execute/test_defects4j.py` is an empty stub** — the Defects4J
   backend has no test coverage. (The Maven backend is covered by
   `tests/execute/test_maven.py`, which mocks `mvn` via `_execute`; that file's
   `conftest.py` adds `multiplex/` to `sys.path` so the flat-import backend
   module is importable — the pattern to copy for a Defects4J test.)

Recently fixed (kept here so stale references elsewhere are recognizable):
- The `prompts` dict in `__main__.py` used to read **all** `system_prompts`
  keys unconditionally, so any missing key crashed every run with `KeyError` —
  the shipped example config itself crashed this way. Now only the selected
  approach's keys are required, validated up front via `multiplex/prompts.py`.
- `execute/maven.py` used to be broken (wrong-arity `rewrite_method` call, never
  ran `mvn test`, passed a directory to `check_mutant_compilable`). It now
  mirrors `execute/defects4j.py` and drives the runnable example (§ Example).

Behavioral gotchas — by design (or at least current design), be aware:

- `<projectroot>/output/` is **deleted without prompting** at every run start
  (the confirmation prompt in `__main__.py` is commented out, answer
  hard-coded to `"y"`).
- The target source file is mutated **in place** during execution; it is
  backed up to `<filename>.orig` and restored at run end, but a crash mid-run
  can leave a mutant in the working tree (the `.orig` file remains for manual
  restore).
- "Compilable" means *parses without tree-sitter ERROR nodes* — no compiler
  runs; type errors and unresolved symbols count as compilable.
- An invalid `mutation.approach` value, or a missing/empty required
  `system_prompts` key for the chosen approach, raises `SystemExit` at startup
  (before the output wipe). Only the selected approach's prompt keys are
  required — see `multiplex/prompts.py`.
- Mutahunter prompts are not bundled (licensing); the user pastes them into
  the config. Running the `mutahunter` approach without them fails fast with a
  clear message.
