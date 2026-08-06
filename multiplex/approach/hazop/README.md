# HAZOP Configuration

The HAZOP configuration requires the `config.yml` file to contain the following:
Update the prompts to suite your chosen language.

```yaml
mutation:
    approach: hazop

system_prompts:
    hazop_describe_process: |
        When given a Java method, describe the intent of the code in a line-by-line manner, as concisely as possible.

        Explain what the code does, not how it is written.
        End each line with a comma and don't use commas anywhere else.
        Break the explanation into line-numbered steps and return the line-numbered steps.
    hazop_identify_deviations: |
        For each numbered description, output one version of the string where one of the rules has changed.
        The rule must be changed using one of the "guidewords" from HAZOP.
        The guidewords and their interpretation is delimited by ###, in the form guideword - interpretation.
        That is, everything before - is the guideword and everything after is the meaning.

        ###

        No (not, none) - None of the design intent is achieved
        More (more of, higher) - Quantitative increase in a parameter
        Less (less of, lower) - Quantitative decrease in a parameter
        As well as (more than) - An additional activity occurs
        Part of - Only some of the design intention is achieved
        Reverse - Logical opposite of the design intent occurs
        Other than (other) - Complete substitution (another activity takes place or an unusual activity occurs or uncommon condition exists)

        ###

        Please output each new rule, as a csv line, without headings in the format:
        "number, original_rule, guideword (CAPITALIZED), changed_rule"
    hazop_implement_deviations: |
        You are a code generator.
        When given a description, re-implement the method but with the incorrect behavior/defect as described in the description.

        Include a concise code comment to describe the implemented defect.
        Output the defective Java code only and nothing else.
```
