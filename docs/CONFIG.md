# Configuration Reference

*multiplex* takes a single YAML config file:
`uv run ./multiplex ./path/to/config.yml`.
Template: [`examples/config.yml`](../examples/config.yml).

All keys below are read unconditionally by `multiplex/__main__.py` — a missing
key raises `KeyError` at startup, even for approaches you are not running.

## `project`

| Key | Type | Meaning |
|-----|------|---------|
| `projectroot` | path | Root of the Java project under test. `output/` is created (and **wiped every run**) inside it. |
| `filename` | path | The `.java` source file containing the method under test. Backed up to `<filename>.orig` during the run. |
| `method` | string | Name of the method (or constructor) to mutate. |
| `line` | int | 1-based line number of the method **name identifier** in `filename` (not annotations above it). Both `method` and `line` must match for extraction to succeed; disambiguates overloads. |
| `runtool` | `mvn` \| `d4j` | Execution backend. `d4j` (Defects4J) is the complete one; `mvn` is currently broken (DEVELOPMENT.md § Known issues). |

## `mutation`

| Key | Type | Meaning |
|-----|------|---------|
| `approach` | `basic` \| `hazop` \| `stpa` \| `mutahunter` \| `llmorpheus` | Mutant-generation approach. Any other value prints "Invalid approach" and continues to the execution phase (which then fails on the missing mutants dir). |

## `llm`

| Key | Type | Meaning |
|-----|------|---------|
| `model` | string | LiteLLM model string, e.g. `ollama/gpt-oss:20b`. |
| `endpoint` | URL | LLM API endpoint, e.g. `http://127.0.0.1:11434`. If the string contains `azure`, Azure env vars are set automatically. |
| `token_env_var` | string or empty | **Name** of the environment variable holding the API key — never the key itself. Leave empty for keyless local endpoints (e.g. Ollama). The named var must exist or startup fails with KeyError. |

Note: the top-level README shows this key as `tokenenvvar`; the code and
example config use `token_env_var`. `token_env_var` is correct.

## `system_prompts`

All nine keys are required (multi-line YAML strings, typically `|` blocks).
User prompts are constructed in code; only system prompts live in config.

| Key | Used by |
|-----|---------|
| `basic_generate_mutants` | basic |
| `hazop_describe_process` | hazop step 1 (line-by-line description) |
| `hazop_identify_deviations` | hazop step 2 (guideword mutation; must instruct CSV output `number, original_rule, GUIDEWORD, changed_rule`) |
| `hazop_implement_deviations` | hazop step 3 (code generation) |
| `stpa_describe_control_flow` | stpa step 1 (GraphViz DOT control diagram) |
| `stpa_identify_ucas` | stpa step 2 (numbered UCA list) |
| `stpa_implement_ucas` | stpa step 3 (code generation) |
| `mutahunter_generate_mutants` | mutahunter — **not bundled**; users must paste Mutahunter's own prompt text (licensing restriction). Response must be YAML with `mutants: [{mutated_code, line_number}]`. |
| `llmorpheus_system` | llmorpheus (per-placeholder replacement generation) |

Output-format expectations matter: downstream parsing is brittle string/CSV/
YAML/regex handling (see MODULE_REFERENCE.md), so prompts must pin the exact
output format the next step expects.
