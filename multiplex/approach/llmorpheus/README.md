# LLMorpheus Configuration

The LLMorpheus configuration requires the `config.yml` file to contain the following:
Update the prompts for your chosen language.

```yaml
mutation:
    approach: llmorpheus 

system_prompts:
    llmorpheus_system: |
        You are an expert in mutation testing. Your job is to make small changes to a project's code in order to find weaknesses in its test suite. 
        If none of the tests fail after you make a change, that indicates that the tests may not be as effective as the developers might have hoped, and provide them with a starting point for improving their test suite.   
```
