from transformers import pipeline, AutoTokenizer
import torch

from services.AiProvider import AiProvider
from services.AppData import AppData
from services.Logger import _log


class SentimentAnalysisProvider(AiProvider):
    def __init__(self, api_key=None):
        super().__init__()  # Initialize the parent class

        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("huggingface")
        if not self.api_key:
            raise ValueError("API key is required for Hugging Face API")

        # Device configuration: use GPU if available, otherwise fallback to CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Define model details and load the sentiment analysis pipeline
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        # Define the pipeline for sentiment analysis
        self.pipe = pipeline(
            task="sentiment-analysis",
            model=self.model_name,
            tokenizer=self.tokenizer,
            device=(
                0 if torch.cuda.is_available() else -1
            ),  # Set device for the pipeline
        )

    def ask(self, prompt: str) -> dict[str, str]:
        try:
            _log("Performing sentiment analysis with HuggingFace.")

            # Perform sentiment analysis
            response = self.pipe(prompt)

            # Prepare the response in the same format
            return {
                "response": self._format_response(prompt, response),
                "provider": "HuggingFace",
            }
        except Exception as e:
            _log(f"Error during sentiment analysis: {str(e)}", level="ERROR")
            return None

    def _format_response(self, prompt: str, response: list[dict]) -> str:
        # Format the sentiment analysis result into a readable string
        sentiment = response[0]["label"]
        confidence = response[0]["score"]
        return f"Text: '{prompt}'\nSentiment: {sentiment}\nConfidence: {confidence:.2f}"

    def _clean_response(self, response: str) -> str:
        # No cleaning needed for sentiment analysis, but maintaining the method for structure
        return response.strip()
