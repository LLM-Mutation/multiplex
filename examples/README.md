# Example run

A self-contained, end-to-end example of *multiplex*.

```bash
# from the repo root
uv run multiplex ./examples/config.yml
```

## What it does

Mutates one method — `com.example.Classifier.classify` in the small Maven
project under [`project/example/`](project/example) — using the **basic**
approach, then runs that project's JUnit tests against each mutant with the
**mvn** backend to see which mutants survive.

## Prerequisites

- `mvn` and a JDK **11 or newer** on your `PATH` (the `mvn` runtool runs
  `mvn clean test`; the project targets Java 11). If `mvn` uses an older JDK —
  e.g. via `JAVA_HOME` — the build fails with "release version 11 not
  supported"; point `JAVA_HOME` at a JDK 11+ or lower `maven.compiler.release`
  in `project/example/pom.xml`.
- A running [Ollama](https://ollama.com) serving the model named in
  `config.yml` under `llm.model` (default `gpt-oss:20b`):

  ```bash
  ollama pull gpt-oss:20b     # or edit llm.model to a model you already have
  ```

  Any LiteLLM-supported provider works — edit the `llm` section of
  `config.yml` (`model`, `endpoint`, `token_env_var`).

## Output

Written under `project/example/output/basic-mutants/`:

- `mutant_N.java` — each generated mutant (the mutated method body).
- `mutant_summary.csv` — one row per mutant with columns
  `MUTANT, EQUIVALENCE, COMPILABLE, SURVIVES`. A surviving mutant is one the
  test suite failed to catch.

These run artifacts (plus the `*.orig` source backup and Maven `target/`) are
git-ignored.

## Trying another approach

Prompt sets are optional per approach, so you can switch `mutation.approach` in
`config.yml` to `hazop` or `stpa` without editing anything else — their prompts
are already included. `mutahunter` and `llmorpheus` need their own prompts added
first (see the comments in `config.yml` and the top-level README).
