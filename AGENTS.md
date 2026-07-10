# AGENTS.md

Guidance for AI coding agents working in this repository.

*multiplex* is a modular framework for prototyping LLM-based mutation testing. One run mutates a single Java method (located via tree-sitter), generates mutants with an LLM, splices each mutant back into the source file, and runs the target project's tests to see which mutants are killed.

## Documentation map

Task-scoped docs live in `docs/` — start at [docs/README.md](docs/README.md) and load only the file relevant to your task instead of reading source:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — pipeline, approaches, execution backends, output artifacts.
- [docs/MODULE_REFERENCE.md](docs/MODULE_REFERENCE.md) — every function's signature, behavior, and side effects.
- [docs/CONFIG.md](docs/CONFIG.md) — full `config.yml` schema.
- [docs/EXTENDING.md](docs/EXTENDING.md) — checklists for adding approaches, execution backends, or LLM providers.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — setup, conventions, CI, known bugs/gotchas.

## Commands

```bash
uv sync -p 3.13                  # install deps (pin 3.13: tiktoken fails to build on 3.14)
uv run pytest tests              # all tests — must run from repo root (relative resource paths)
uv run pytest tests/checks/test_compiles.py::test_name      # one test
uv run ruff check .              # lint (matches CI)
uv run ./multiplex ./path/to/config.yml                     # run the tool
```

## Critical rules

- **Import convention**: the tool runs as a directory (`uv run ./multiplex`), so `multiplex/` itself is on `sys.path`. Modules inside `multiplex/` import each other **without** the package prefix (`from model import Model`); tests import **with** it (`from multiplex.checks... import ...`). Match the file you are editing. Rationale in `docs/DEVELOPMENT.md`.
- Pipeline entry point and dispatch: `multiplex/__main__.py`. Adding an approach touches three places (new `approach/<name>/controller.py` package + `APPROACH_PROMPT_KEYS` entry in `multiplex/prompts.py` + dispatch branch). Only the selected approach's `system_prompts` keys are required; `resolve_prompts` validates them (and the approach name) up front, raising `SystemExit` before any destructive step. See `docs/EXTENDING.md`.
- `<projectroot>/output/` is wiped at the start of every run; the target source file is edited in place and restored from a `.orig` backup.
- tree-sitter versions are pinned; do not bump them casually.
- A runnable example lives in `examples/`: `uv run multiplex ./examples/config.yml` (self-contained Maven project, needs `mvn` + a JDK + a running Ollama). See `docs/DEVELOPMENT.md` § Example.
