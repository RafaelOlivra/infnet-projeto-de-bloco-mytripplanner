import requests
import bs4
import streamlit as st
from transformers import pipeline
import torch

from services.AiProvider import AiProvider
from services.AppData import AppData


class HuggingFaceProvider(AiProvider):
    def __init__(self, api_key=None):
        # Set the API key, either from the environment or directly from the parameter
        self.api_key = api_key or AppData().get_api_key("HUGGINGFACE_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for Hugging Face API")

        self.base_url = "https://api-inference.huggingface.co/models/"
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model = {}
        self.model.mode = "text-generation"
        self.model.name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.model.prompt = super().prompt

        if not self.api_key:
            raise ValueError("API key is required for Hugging Face API")

    def ask(self, message: str) -> dict:
        generator = pipeline(self.model.mode, model=self.model.name)
        device = torch.device("cuda")

        pipe = pipeline(
            self.model.mode,
            model=self.model.name,
            torch_dtype=torch.bfloat16,
            device=self.device,
        )
