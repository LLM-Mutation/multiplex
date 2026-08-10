Adding a Programming Language
=============================

To add compatability for a programming language in *multiplex*, you must create a language specification in ``multiplex/languages/__init__.py``.

The language should be added to the ``_REGISTRY`` as shown below:

.. code-block:: Python
   _REGISTRY = {
    "java": LanguageSpec(
        name="java",
        extension=".java", # the file extension for Java code files
        ts_language=Language(ts_java.language()), # the TreeSitter Java library
        def_node_types=frozenset({"method_declaration", "constructor_declaration"}), # the structures to mutate
        comment_node_types=frozenset({"comment", "line_comment", "block_comment"}), # comments to ignore
        fence="java", # the language decription used for code fences
        noun="Java method", # noun for inserting in prompts
        label="Java", # internal label
    ),
   }

This example shows the Java language description using the TreeSitter library nodes to describe specific code structures such as comments and method definitions to enable *multiplex* to mutate the relevant code.

The user should import the relevant TreeSitter library for the language they are adding.
Currently, *multiplex* can only support languages supported by TreeSitter.

