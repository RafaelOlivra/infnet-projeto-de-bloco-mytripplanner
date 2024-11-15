import google.generativeai as genai

from services.AiProvider import AiProvider
from services.AppData import AppData
from services.Logger import _log


class GeminiProvider(AiProvider):
    def __init__(self, api_key=None):
        super().__init__()  # Initialize the parent class

        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("googlegemini")
        if not self.api_key:
            raise ValueError("API key is required for Google Gemini API")

        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-1.5-flash"

    def generate(self) -> dict[str, str]:
        prompt = self._generate_final_prompt()

        try:
            _log("Generating content with Gemini.")

            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(prompt)

            return {"response": response.text, "provider": "Google Gemini"}
        except Exception as e:
            _log(f"{str(e)}", level="ERROR")
            return None
