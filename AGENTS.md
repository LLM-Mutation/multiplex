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

- **Import convention**: modules inside `multiplex/` import each other **without** the package prefix (`from model import Model`); tests import **with** it (`from multiplex.checks... import ...`). Match the file you are editing. Rationale in `docs/DEVELOPMENT.md`.
- Adding an approach touches three places (package + prompt keys + dispatch); all `system_prompts` config keys are read unconditionally at startup. See `docs/EXTENDING.md`.
- tree-sitter versions are pinned; do not bump them casually.
- Check `docs/DEVELOPMENT.md` § Known issues before building on `execute/maven.py` (broken) or the STPA mutant loop (off-by-one); `execute/defects4j.py` is the reference execution backend.
