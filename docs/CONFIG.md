# Configuration Reference

*multiplex* takes a single YAML config file:
`uv run ./multiplex ./path/to/config.yml`.
Templates: [`examples/config-java.yml`](../examples/config-java.yml),
[`examples/config-python.yml`](../examples/config-python.yml).

Only the keys the selected `mutation.approach` needs are required. `project`,
`mutation`, and `llm` keys are always required; `system_prompts` keys are
required per-approach (see that section). Missing required keys fail fast at
startup with an actionable `SystemExit`, before any output is wiped.

## `project`

| Key | Type | Meaning |
|-----|------|---------|
| `language` | `java` \| `python` | Source language of the file under test. **Optional; defaults to `java`** (existing configs need no change). Selects the tree-sitter grammar, the definition node types extracted, the artifact/mutant file extension, and the code-fence/prompt wording. An unknown value fails fast at startup with a `SystemExit`. |
| `projectroot` | path | Root of the project under test. `output/` is created (and **wiped every run**) inside it. |
| `filename` | path | The source file containing the method/function under test (`.java` or `.py`). Backed up to `<filename>.orig` during the run. |
| `method` | string | Name of the method/constructor (Java) or function (Python) to mutate. |
| `line` | int | 1-based line number of the method/function **name identifier** in `filename` (not annotations/decorators above it). Both `method` and `line` must match for extraction to succeed; disambiguates overloads. |
| `runtool` | `mvn` \| `d4j` \| `pytest` | Execution backend. `mvn` runs a plain Maven project (`mvn clean test`); `d4j` targets a Defects4J checkout (needs the `defects4j` CLI + `JDK_11`); `pytest` runs `python -m pytest <projectroot>` (a mutant survives if pytest exits 0). `mvn` drives the Java `examples/` setup and `pytest` the Python one. |

## `mutation`

| Key | Type | Meaning |
|-----|------|---------|
| `approach` | `basic` \| `hazop` \| `stpa` \| `mutahunter` \| `llmorpheus` | Mutant-generation approach. An unknown value fails fast at startup with a `SystemExit` listing the valid approaches. |

## `llm`

| Key | Type | Meaning |
|-----|------|---------|
| `model` | string | LiteLLM model string, e.g. `ollama/gpt-oss:20b`. |
| `endpoint` | URL | LLM API endpoint, e.g. `http://127.0.0.1:11434`. If the string contains `azure`, Azure env vars are set automatically. |
| `token_env_var` | string or empty | **Name** of the environment variable holding the API key — never the key itself. Leave empty for keyless local endpoints (e.g. Ollama). The named var must exist or startup fails with KeyError. |

## `system_prompts`

Multi-line YAML strings (typically `|` blocks). Only the keys used by the
selected `mutation.approach` are required — prompts for other approaches may be
omitted. The approach→required-keys mapping is `APPROACH_PROMPT_KEYS` in
`multiplex/prompts.py`; a missing or empty required key raises a `SystemExit`
naming it. User prompts are constructed in code; only system prompts live in
config.

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
