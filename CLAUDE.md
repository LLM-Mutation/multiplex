# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

*multiplex* is a modular framework for prototyping and comparing LLM-based mutation testing approaches. One run mutates a single Java method (located via tree-sitter), generates mutants with an LLM, injects each mutant back into the source file, and runs the target project's tests to determine which mutants are killed.

## Documentation map

Detailed docs live in `docs/` — load only the file relevant to the task instead of reading source:

- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — end-to-end pipeline, approaches, execution backends, output artifacts.
- [docs/MODULE_REFERENCE.md](docs/MODULE_REFERENCE.md) — every function's signature, behavior, and side effects.
- [docs/CONFIG.md](docs/CONFIG.md) — full `config.yml` schema.
- [docs/EXTENDING.md](docs/EXTENDING.md) — checklists for adding approaches, execution backends, or LLM providers.
- [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md) — setup, conventions, CI, and the current list of known bugs/gotchas.

## Commands

```bash
uv sync -p 3.13                  # install deps (pin 3.13: tiktoken fails to build on 3.14)
uv run pytest tests              # all tests — must run from repo root (relative resource paths)
uv run pytest tests/checks/test_compiles.py::test_name      # one test
uv run ruff check .              # lint
uv run ./multiplex ./path/to/config.yml                     # run the tool
```

## Critical conventions

- **Import convention**: the tool runs as a directory (`uv run ./multiplex`), so `multiplex/` itself is on `sys.path`. Modules inside `multiplex/` import each other **without** the package prefix (`from model import Model`, `from util.io import ...`); tests import **with** it (`from multiplex.checks... import ...`). Match the style of the file you are editing.
- Pipeline entry point and dispatch: `multiplex/__main__.py`. Adding an approach touches three places (new `approach/<name>/controller.py` package, a `APPROACH_PROMPT_KEYS` entry in `multiplex/prompts.py`, dispatch branch in `__main__.py`) — see docs/EXTENDING.md.
- Only the selected approach's `system_prompts` keys are required; `resolve_prompts` in `multiplex/prompts.py` validates them (and the approach name) up front, raising `SystemExit` before any destructive step.
- `<projectroot>/output/` is wiped at the start of every run; the target source file is edited in place and restored from a `.orig` backup.
- Before relying on `execute/maven.py` or the STPA mutant loop, check docs/DEVELOPMENT.md § Known issues — both have verified bugs (Maven backend is broken; use `execute/defects4j.py` as reference).
