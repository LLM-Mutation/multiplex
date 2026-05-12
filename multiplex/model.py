import os

from litellm import completion



class Model:

    def __init__(self, model=None, endpoint=None, api_key_var=None):
        self.model = model
        self.endpoint = endpoint
        if api_key_var is not None and api_key_var != '':
            self.api_key = os.environ[api_key_var]

            if "azure" in endpoint:
                os.environ["AZURE_AI_API_BASE"] = endpoint
                os.environ["AZURE_AI_API_KEY"] = os.environ[api_key_var]


        print("Model:", self.model)


    def current_model(self):
        """Return current model"""
        return self.model

    def make_request(self, messages):
        """Make request to current LLM."""
        print("Sending request to LLM:")
        response = completion(model=self.model, messages=messages)
        print("Response received from LLM:")

        return response.choices[0].message.content
