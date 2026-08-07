Included Modules
================

Languages
---------
*multiplex* currently includes Java and Python compatibility.
These are selected per run through the configuration file through ``project.language``.
Instructions for adding additional language compatibility can be found in :doc:`adding-language`.

Mutant Generation
-----------------
*multiplex* currently includes the following five mutant generation modules:

+-------------+--------------------+--------------------------------------------+
| Approach    | *multiplex* config | Description                                |
+=============+====================+============================================+
| STPA        | stpa               | Implements Systems Theoretic Process       | 
|             |                    | Analysis mutant generation approach        |
+-------------+--------------------+--------------------------------------------+
| HAZOP       | hazop              | Implements HAZard and OPerability study    |
|             |                    | mutant generation approach                 |
+-------------+--------------------+--------------------------------------------+
| Unguided    | basic              | Implements an unguided mutant generation   |
|             |                    | approach                                   |
+-------------+--------------------+--------------------------------------------+
| LLMorpheus  | llmorpheus         | Implements the LLMorpheus approach         |
+-------------+--------------------+--------------------------------------------+
| Mutahunter  | mutahunter         | Implements the mutahunter approach         |
+-------------+--------------------+--------------------------------------------+

Execution and Evaluation
------------------------
*multiplex* currently offers the following for mutant execution and evaluation.

+-------------+--------------------+--------------------------------------------+
| Framework   | *multiplex* config | Description                                |
+=============+====================+============================================+
| Maven       | mvn                | Execute mutants using a Maven runner       |
+-------------+--------------------+--------------------------------------------+
| Defects4J   | d4j                | Framework to execute test suites from      |
+-------------+--------------------+--------------------------------------------+
| PyTest      | pytest             | Execute mutants using PyTest runner        |
+-------------+--------------------+--------------------------------------------+


