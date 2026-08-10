Adding an Execution and Evaluation Module
=========================================

Users can add test runners and test execution frameworks to enable *multiplex* to execute and evaluate mutants in a diverse set of projects. 

Using the ``maven`` test runner as an example, users can specifiy how *multiplex* should execute the mutants.

The user should specify the CLI commands that *multiplex* requires to execute the test suite using the framework and ensure the relevant file paths are specified.

