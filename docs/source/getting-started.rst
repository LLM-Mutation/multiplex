Getting Started
===============

Requirements
------------
Using the *multiplex* tool requires the following:

- UV Dependency Management: Follow installation instructions at `uv`_.
- ``yq`` for parsing yaml config files with bash

.. _uv: https://github.com/astral-sh/uv


Installation
------------

1. Clone the repository:
   
    .. code-block:: bash
    
        git clone https://github.com/LLM-Mutation/multiplex.git
   
2. Install the dependencies and activate environment:
    
    .. code-block:: bash

        cd multiplex
        uv sync 
        source .venv/bin/activate
        cd ..
   

Configuration
-------------

*multiplex* is configured using a ``yaml`` file.
Users can use the example configuration file in the ``examples/`` to set up their project. 
This section overviews the content required in the configuration file.

 
Project
^^^^^^^

This section includes the details about the project and method under test, including reference to the module for running and parsing the tests.

LLM
^^^

To configure the LLM, update the config.yml file. 
Below is an example for ``gpt-oss:20b``, run locally using Ollama.
To use `gpt-oss:20b`, download Ollama, and run `ollama pull gpt-oss:20b`. 
Ensure Ollama is running (``ollama serve``) when using *multiplex* for this example.

.. code-block:: yaml
    
    llm:
        model: ollama/gpt-oss:20b
        endpoint: http://127.0.0.1:11434
        token_env_var: # env var name storing token (NOT TOKEN)

.. important::
    Security Note: Never hardcode API keys in your config file. Set an environment variable and reference its name in the token_env_var field.

System Prompts
^^^^^^^^^^^^^^

.. note::
    Mutahunter Module prompts must be added by user due to licensing restrictions. - `User Prompt Link`_ / `System Prompt Link`_.

.. _User Prompt Link:: https://github.com/codeintegrity-ai/mutahunter/blob/main/src/mutahunter/core/templates/mutant_generation/mutator_user.txt

.. _System Prompt Link:: https://github.com/codeintegrity-ai/mutahunter/blob/main/src/mutahunter/core/templates/mutant_generation/mutator_system.txt

The System Prompts are included in the configuration file for easy updating. 
The user prompts are constructed within *multiplex* so users should modify or create modules to alter these.

Running *multiplex*
-------------------
Once configured and modules are set up, users can run *multiplex* using the following command:


.. code-block:: bash

    uv run /path/to/multiplex ./path/to/config.yml


Included examples
^^^^^^^^^^^^^^^^^

Self-contained examples are included for both supported languages, each mutating
a small project with the ``basic`` approach. With a running Ollama instance
(``ollama pull gpt-oss:20b``, ``ollama serve`` and edit ``llm.model`` in the config), run from the repo
root:

.. code-block:: bash

    uv run ./multiplex ./examples/config-java.yml     # Java  (needs mvn + a JDK on PATH)
    uv run ./multiplex ./examples/config-python.yml   # Python (uses pytest via uv run)


Results are written to the project's ``output/<approach>-mutants/mutant_summary.csv``. See `examples/README.md`_ for
details.

.. examples/README.md:: https://github.com/LLM-Mutation/multiplex/blob/main/examples/README.md

Optional: Marv output
^^^^^^^^^^^^^^^^^^^^^
If you want Marv-compatible output, install Marv and make sure its binary is
on your ``PATH`` before running ``multiplex``:

.. code-block:: bash

    go install github.com/SecretSheppy/marv@latest
    export PATH="$HOME/go/bin:$PATH"
    marv --version

Inside the project, run 

.. code-block:: bash

    marv init -f generic


and update the .marv.yml file to the following:

.. code-block:: yaml
    marv:
        port: 8080
        output:
            path: .marv
            merge: false
        review-dir: .marv/reviews
    generic:
        framework: "multiplex"
        marv-json: "output/marv.json"
        src-dir: "output"


Then run *multiplex* with the ``--marv`` flag to generate ``output/marv.json``
alongside the usual mutant files and summary:

.. code-block:: bash

    uv run multiplex --marv ./examples/config.yml


Marv can then read the generated ``marv.json`` from the project output folder by running the ``marv`` command.

