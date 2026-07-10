# docs/ — Agent Documentation Index

Documentation for humans and AI agents working on *multiplex*. Each file is
self-contained: **load only the file(s) relevant to your task** rather than
reading source code or every doc.

| File | Read it when you need to... |
|------|-----------------------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Understand the pipeline end-to-end: data flow, output artifacts, how mutants are injected and evaluated. |
| [MODULE_REFERENCE.md](MODULE_REFERENCE.md) | Call or modify an existing function — every public function's signature, inputs, outputs, and side effects, without opening source files. |
| [CONFIG.md](CONFIG.md) | Read, write, or validate a `config.yml` — full schema, every key. |
| [EXTENDING.md](EXTENDING.md) | Add a new mutant-generation approach, execution backend, or LLM provider — exact checklists of files to touch. |
| [DEVELOPMENT.md](DEVELOPMENT.md) | Set up, run commands, run tests, follow conventions, or avoid known gotchas and open bugs. |

Quick orientation (enough for trivial tasks, no further reading needed):

- *multiplex* mutates **one Java method** per run: extract it with tree-sitter,
  ask an LLM to generate mutants, splice each mutant back into the source file,
  run the project's tests, and record which mutants survive.
- Entry point: `multiplex/__main__.py`, run as `uv run ./multiplex ./config.yml`.
- Python >= 3.13 (pin 3.13 — see DEVELOPMENT.md), deps via `uv`, lint via `ruff`,
  tests via `pytest` from the repo root.
- Code inside `multiplex/` imports siblings **without** the `multiplex.` prefix
  (`from model import Model`); tests import **with** it
  (`from multiplex.checks... import ...`). See DEVELOPMENT.md before editing imports.
