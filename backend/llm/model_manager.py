import requests

from backend.core.config import OLLAMA_HOST, LLM_MODEL


class ModelManager:
    def __init__(
        self,
        host: str = OLLAMA_HOST,
        model: str = LLM_MODEL,
    ):
        self.host = host.rstrip("/")
        self.model = model

    def is_ollama_available(self) -> bool:
        try:
            response = requests.get(
                self.host,
                timeout=5,
            )

            return response.ok

        except requests.RequestException:
            return False

    def list_models(self) -> list[str]:
        response = requests.get(
            f"{self.host}/api/tags",
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        return [
            model["name"]
            for model in data.get("models", [])
        ]

    def is_model_available(self) -> bool:
        try:
            models = self.list_models()

            return any(
                model == self.model
                for model in models
            )

        except requests.RequestException:
            return False

    def get_model(self) -> str:
        return self.model

    def get_status(self) -> dict:
        ollama_available = self.is_ollama_available()

        if not ollama_available:
            return {
                "ollama": False,
                "model": self.model,
                "model_available": False,
            }

        model_available = self.is_model_available()

        return {
            "ollama": True,
            "model": self.model,
            "model_available": model_available,
        }