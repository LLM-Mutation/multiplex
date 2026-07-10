# 🪲 _multiplex_: A Modular LLM-based Mutation Framework

[![Tests](https://github.com/LLM-Mutation/multiplex/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/LLM-Mutation/multiplex/actions/workflows/test.yml)
[![Ruff](https://github.com/LLM-Mutation/multiplex/actions/workflows/ruff.yml/badge.svg)](https://github.com/LLM-Mutation/multiplex/actions/workflows/ruff.yml)


**A tool for prototyping and comparing LLM-based mutation testing approaches.**

 *__multiplex__* has a modular design to enable researchers to build, design and
 test LLM-based Mutation testing approaches in an easy to use framework.

 Multiplex is currently designed to enable mutation at the method level, but
 prompting and further modularisation could support other context levels. 
    Fork this project and add your own modules. 

## Getting Started
### ✅ Requirements
- [ ] UV Dependency Management: Follow installation instructions at [uv](https://github.com/astral-sh/uv).
- [ ] yq for parsing yaml config files with bash

### 👩‍💻 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/LLM-Mutation/multiplex.git
   ```
2. Install the dependencies and activate environment:
   ```bash
   cd multiplex
   uv sync 
   source .venv/bin/activate
   cd ..
   ```

### 🔧 Configuration

*multiplex* is configured using a `yaml` file.
Users can use the example configuration file in the `examples/` to set up their project. 
This section overviews the content required in the configuration file.

#### Project
This section includes the details about the project and method under test, including reference to the module for running and parsing the tests.

#### LLM

To configure the LLM, update the config.yml file. 
Below is an example for `gpt-oss:20b`, run locally using Ollama.
To use `gpt-oss:20b`, download Ollama, and run `ollama pull gpt-oss:20b`. 
Ensure Ollama is running when using *multiplex* for this example.
```
llm:
    model: ollama/gpt-oss:20b
    endpoint: http://127.0.0.1:11434
    token_env_var: # env var name storing token (NOT TOKEN)
```
[IMPORTANT]
Security Note: Never hardcode API keys in your config file. Set an environment variable and reference its name in the tokenenvvar field.

#### System Prompts
**NOTE:** Mutahunter Module prompts must be added by user due to licensing restrictions. - [User Prompt Link](https://github.com/codeintegrity-ai/mutahunter/blob/main/src/mutahunter/core/templates/mutant_generation/mutator_user.txt) / [System Prompt Link](https://github.com/codeintegrity-ai/mutahunter/blob/main/src/mutahunter/core/templates/mutant_generation/mutator_system.txt).

The System Prompts are included in the configuration file for easy updating. 
The user prompts are constructed within *multiplex* so users should modify or create modules to alter these.

### 🏃 Running *multiplex*
Once configured and modules are set up, users can run *multiplex* using the following command:
```bash
uv run /path/to/multiplex ./path/to/config.yml
```

#### Try the bundled example
A self-contained example (a small Maven project mutated with the `basic`
approach) is included. With `mvn` + a JDK on your `PATH` and a running Ollama
(`ollama pull gpt-oss:20b`, or edit `llm.model` in the config), run from the
repo root:
```bash
uv run multiplex ./examples/config.yml
```
Results are written to `examples/project/example/output/basic-mutants/`
(`mutant_summary.csv`). See [`examples/README.md`](examples/README.md) for
details.

## 🧩 Existing Modules
*multiplex* currently includes five mutant generation modules and two execution and evaluation modules:

**Mutant Generation Modules:**
- HAZOP
- STPA
- basic (or unguided)
- LLMorpheus
- Mutahunter (note the user must collect Mutahunter's prompts themselves due to licensing restrictions).

**Execution and Evaluation Modules**
- Maven
- Defects4J (enables users to target specific bugs in the [Defects4J](https://github.com/rjust/defects4j) dataset)

## 🏗️ Adding Modules

### Adding LLM Modules
*multiplex* uses `LiteLLM` to interface with LLMs. Many local options will be configurable directly from the configuration file. 
However, specific LLM providers may require further information.
In this instance, the user should create their own `multiplex/model.py` file and use `LiteLLM` to interact with their provider of choice. 

### Adding Mutant Generation (MG) Approach Modules 
In order to create an MG approach, users should add an MG package to  `multiplex/approach`  containing a `controller.py` file that directs their approach.
It may help users to use the existing modules in `multiplex/approach` as examples as there are single prompt (e.g., basic) and multi-prompt (e.g., HAZOP) examples.


### Adding Execution and Evaluation Modules
Users can add a mutant execution and evaluation class to `multiplex/execute/` that inserts the mutant into the source code file, runs the project's tests with the appropriate build and execution tools, and parses the results to identify which mutants are killed by which tests.

## 💬 Questions and Community
Have a question or found a bug? We’d love to hear from you. Please open an issue in the **Issue Tracker** and we'll get back to you!