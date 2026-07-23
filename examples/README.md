# Example runs

Self-contained, end-to-end examples of *multiplex* — one Java, one Python.

```bash
# from the repo root
uv run ./multiplex ./examples/config-java.yml     # Java
uv run ./multiplex ./examples/config-python.yml   # Python
```

## What the Java example does

Mutates one method — `com.example.Classifier.classify` in the small Maven
project under [`project/java-example/`](project/java-example) — using the
**basic** approach, then runs that project's JUnit tests against each mutant with
the **mvn** backend to see which mutants survive.

## What the Python example does

Mutates one function — `classify` in
[`project/python-example/classifier.py`](project/python-example/classifier.py) —
using the **basic** approach with `project.language: python`, then runs that
project's pytest suite against each mutant with the **pytest** backend. Output
lands under `project/python-example/output/basic-mutants/` (mutant files are
`.py`; the summary CSV columns are identical to the Java run).

Prerequisite: pytest for the active interpreter (already provided by `uv run`)
plus an LLM endpoint as below. The rest of this page describes the Java example.

## Prerequisites

- `mvn` and a JDK **11 or newer** on your `PATH` (the `mvn` runtool runs
  `mvn clean test`; the project targets Java 11). If `mvn` uses an older JDK —
  e.g. via `JAVA_HOME` — the build fails with "release version 11 not
  supported"; point `JAVA_HOME` at a JDK 11+ or lower `maven.compiler.release`
  in `project/java-example/pom.xml`.
- A running [Ollama](https://ollama.com) serving the model named in
  `config-java.yml` under `llm.model` (default `gpt-oss:20b`):

  ```bash
  ollama pull gpt-oss:20b     # or edit llm.model to a model you already have
  ```

  Any LiteLLM-supported provider works — edit the `llm` section of
  `config-java.yml` (`model`, `endpoint`, `token_env_var`).

## Output

Written under `project/java-example/output/basic-mutants/`:

- `mutant_N.java` — each generated mutant (the mutated method body).
- `mutant_summary.csv` — one row per mutant with columns
  `MUTANT, EQUIVALENCE, COMPILABLE, SURVIVES`. A surviving mutant is one the
  test suite failed to catch.

These run artifacts (plus the `*.orig` source backup and Maven `target/`) are
git-ignored.

## Trying another approach

Prompt sets are optional per approach, so you can switch `mutation.approach` in
`config-java.yml` to `hazop` or `stpa` without editing anything else — their
prompts are already included. `mutahunter` and `llmorpheus` need their own
prompts added first (see the comments in `config-java.yml` and the top-level
README).
