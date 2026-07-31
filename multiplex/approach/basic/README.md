# Unguided/Basic Configuration

The unguided or `basic` configuration requires the `config.yml` file to contain the following:
Update the prompts for your chosen language.

```yaml
mutation:
    approach: basic

system_prompts:
    basic_generate_mutants: |
        You are a code generator.
        When given a Java method, re-implement it with a single small behavioral defect (a mutant).
        Change exactly one thing: an operator, a boundary condition, a constant, or a returned value.
        Include a concise code comment describing the injected defect.
        Output the defective Java code only and nothing else.

```
