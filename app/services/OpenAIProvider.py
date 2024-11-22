import time
import openai

from services.AiProvider import AiProvider
from services.AppData import AppData
from services.Logger import _log


class OpenAIProvider(AiProvider):
    def __init__(self, api_key=None):
        super().__init__()  # Initialize the parent class

        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("openai")
        if not self.api_key:
            raise ValueError("API key is required for OpenAI API")

        openai.api_key = self.api_key
        self.model_name = "gpt-4o-mini"
        self.max_tokens = 1500

    def ask(self, prompt: str) -> dict[str, str]:
        try:
            _log("[OpenAI] Generating content...")

            # Count the time taken to generate the content
            start_time = time.time()

            # Call OpenAI's API for text generation
            response = openai.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
            )

            # Calculate the time taken to generate the content
            end_time = time.time()
            time_taken = end_time - start_time

            _log(
                "[OpenAI] Content ready! Time taken: {:.2f} seconds".format(time_taken)
            )

            return {
                "response": response.choices[0].message.content,
                "provider": "OpenAI",
            }
        except Exception as e:
            _log(f"{str(e)}", level="ERROR")
            return None

    def set_max_tokens(self, max_tokens: int):
        self.max_tokens = max_tokens
