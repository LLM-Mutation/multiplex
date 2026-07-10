# Copilot Instructions for multiplex

*multiplex* is a modular framework for prototyping LLM-based mutation testing. One run mutates a single Java method (located via tree-sitter), generates mutants with an LLM, splices each mutant back into the source file, and runs the target project's tests to see which mutants are killed.

## Read the docs before reading source

Detailed, task-scoped documentation lives in `docs/` — load only the file relevant to the task:

- `docs/ARCHITECTURE.md` — end-to-end pipeline, approaches, execution backends, output artifacts.
- `docs/MODULE_REFERENCE.md` — every function's signature, behavior, and side effects.
- `docs/CONFIG.md` — full `config.yml` schema.
- `docs/EXTENDING.md` — checklists for adding approaches, execution backends, or LLM providers.
- `docs/DEVELOPMENT.md` — setup, conventions, CI, and the current list of known bugs/gotchas.

## Commands

```bash
uv sync -p 3.13                  # install deps (pin 3.13: tiktoken fails to build on 3.14)
uv run pytest tests              # all tests — must run from repo root (relative resource paths)
uv run pytest tests/checks/test_compiles.py::test_name      # one test
uv run ruff check .              # lint (matches CI)
uv run ./multiplex ./path/to/config.yml                     # run the tool
```

## Rules that prevent broken changes

- **Import convention**: the tool runs as a directory (`uv run ./multiplex`), so `multiplex/` itself is on `sys.path`. Modules inside `multiplex/` import each other **without** the package prefix (`from model import Model`, `from util.io import ...`); tests import **with** it (`from multiplex.checks... import ...`). Match the style of the file being edited.
- Adding a mutant-generation approach touches three places: a new `multiplex/approach/<name>/` package with `controller.py`, an `APPROACH_PROMPT_KEYS` entry in `multiplex/prompts.py`, and a dispatch branch in `multiplex/__main__.py`. Only the selected approach's `system_prompts` keys are required; `resolve_prompts` validates the approach and its keys up front, raising `SystemExit` before any destructive step.
- Mutant files must be complete replacement methods written to `output/<approach>-mutants/mutant_N.java`; they are spliced verbatim over the original method's byte range.
- tree-sitter versions are pinned (`tree-sitter==0.23.2`, `tree-sitter-java==0.23.5`); do not bump them casually — the parsing code depends on that API.
- A runnable end-to-end example lives in `examples/` (self-contained Maven project, `basic` approach, `mvn` backend): `uv run multiplex ./examples/config.yml`. The STPA mutant loop still drops its last item — check `docs/DEVELOPMENT.md` § Known issues.
- Keep pure logic (parsing, splicing, checks) separate from `model.make_request` call sites — LLM calls are not mocked in tests.
