.. multiplex documentation main file, created by
   sphinx-quickstart on Fri Aug  7 10:42:38 2026.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to *multiplex*
=======================

A tool for prototyping and comparing LLM-based mutation testing techniques.

*multiplex* has a modular design to enable researchers to build, design and test LLM-based Mutation testing approaches in an easy to use framework.

Multiplex is currently designed to enable mutation at the method level, but
prompting and further modularisation could support other context levels. 
Fork this project and add your own modules.

Questions and Community
-----------------------
Have a question or found a bug? We’d love to hear from you. Please open an issue in the **Issue Tracker** and we'll get back to you!

Citing this tool
----------------------
If you use this tool in your work or research, please cite as follows:

.. code-block:: latex

    @inproceedings{Maton2026a,
      author    = {Maton, Megan and Kapfhammer, Gregory M. and McMinn, Phil},
      title     = {multiplex: A Modular LLM-based Mutation Framework},
      booktitle = {Proceedings of the International Conference on Automated Software Engineering (ASE) - Tools and Datasets Track},
      year      = {2026},
    }

If you are specifically interested in Hazard Analysis approaches for guiding LLM-based mutant generation, please consider reading (and if relevant, citing):

.. code-block:: latex

    @inproceedings{Maton2026,
      author    = "Maton, Megan and Kapfhammer, Gregory M. and McMinn, Phil",
      title     = "Empirically Comparing Hazard-Guided LLM Mutation Techniques with Existing LLM- and
                   Rule-Based Approaches",
      booktitle = "International Conference on Evaluation and Assessment in Software Engineering (EASE)",
      year      = "2026"
    }

.. toctree::
   :hidden:
   :caption: Home

.. toctree::
   :hidden:
   :maxdepth: 3
   :caption: Introduction

   getting-started
   existing-modules
   configuration

.. toctree::
   :hidden:
   :maxdepth: 2
   :caption: Extending

   adding-language
   adding-mutant-generation
   adding-execution-and-evaluation

.. toctree:: 
   :hidden:
   :maxdepth: 2
   :caption: Development

   architecture
