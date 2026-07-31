# STPA Configuration

The STPA configuration requires the `config.yml` file to contain the following:
Update the prompts for your chosen language.

```yaml
mutation:
    approach: stpa

system_prompts:
    stpa_describe_control_flow: |
        You describe Java methods as control flow diagrams.
        When given a Java Method, create a written description in the DOT language used in GraphViz of the control structure.
        Use human readable labels and descriptions for each node.
        Output the control diagram only, and nothing else.
    stpa_identify_ucas: |
        Identify 10 different Unsafe Control Actions (UCAs) within the control diagram described in DOT language, referencing the code, using each of the guidewords delimited by ### below:

        ###
        * provides
        * does not provide
        * too early
        * too late
        * out of order
        * stopped too soon
        * applied for too long

        ###

        You must describe each UCA in the format: <Variable or Structure><ControlAction><Guideword><Context>

        An example of this is:
        variable x calculated out of order when sorting has not occurred.

        Output the numbered list of UCAs with no empty lines, and nothing else.
    stpa_implement_ucas: |
        You are a code generator.
        When given a description, re-implement the method but with the incorrect behavior/defect as described in the description.

        Include a concise code comment to describe the implemented defect.
        Output the defective Java code only and nothing else.

```
