from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
import torch

from services.AiProvider import AiProvider
from services.AppData import AppData
from services.Logger import _log


class HuggingFaceProvider(AiProvider):
    def __init__(self, api_key=None):
        super().__init__()  # Initialize the parent class

        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("huggingface")
        if not self.api_key:
            raise ValueError("API key is required for Hugging Face API")

        # Device configuration: use GPU if available, otherwise fallback to CPU
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Define model details and load tokenizer and model
        self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        # Define the pipeline for text generation
        self.pipe = pipeline(
            task="text-generation",
            model=self.model_name,
            tokenizer=self.tokenizer,
            device=(
                0 if torch.cuda.is_available() else -1
            ),  # Set device for the pipeline
            torch_dtype=torch.bfloat16 if torch.cuda.is_available() else torch.float32,
        )

    def generate(self) -> dict[str, str]:
        # Generate text based on the message
        prompt = self._generate_final_prompt()

        message = [
            {
                "role": "system",
                "content": "You are a friendly chatbot that help users with their tasks.",
            },
            {"role": "user", "content": prompt},
        ]
        prompt = self.pipe.tokenizer.apply_chat_template(
            message, tokenize=False, add_generation_prompt=False
        )

        try:
            _log("Generating content with HuggingFace.")

            response = self.pipe(
                prompt,
                max_new_tokens=256,
                do_sample=True,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
            )

            # Generate a response using the Hugging Face pipeline
            # response = self.pipe(prompt, max_length=1000, max_new_tokens=256)

            # Clean the response and return it
            return {
                "response": self._clean_response(response[0]["generated_text"]),
                "provider": "HuggingFace",
            }
        except Exception as e:
            _log(f"{str(e)}", level="ERROR")
            return None

    def _clean_response(self, response: str) -> str:
        # Remove the system message from the response
        return response.split("\n<|assistant|>\n")[1].strip()
