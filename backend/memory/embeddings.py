from pathlib import Path
from typing import Optional

from backend.core.config import MODELS_DIR


class EmbeddingModel:
    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        cache_dir: Optional[Path] = None,
    ):
        self.model_name = model_name
        self.cache_dir = cache_dir or (
            MODELS_DIR / "embeddings"
        )

        self._model = None

    def _load_model(self):
        if self._model is not None:
            return

        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as error:
            raise RuntimeError(
                "sentence-transformers is not installed. "
                "Install it with: "
                "pip install sentence-transformers"
            ) from error

        self.cache_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._model = SentenceTransformer(
            self.model_name,
            cache_folder=str(self.cache_dir),
        )

    def encode(
        self,
        text: str,
    ) -> list[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        self._load_model()

        embedding = self._model.encode(
            text.strip(),
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embedding.tolist()

    def encode_many(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        if not texts:
            return []

        if any(
            not text or not text.strip()
            for text in texts
        ):
            raise ValueError(
                "All texts must contain valid content"
            )

        self._load_model()

        embeddings = self._model.encode(
            texts,
            convert_to_numpy=True,
            normalize_embeddings=True,
        )

        return embeddings.tolist()

    def similarity(
        self,
        first: list[float],
        second: list[float],
    ) -> float:
        if len(first) != len(second):
            raise ValueError(
                "Embeddings must have the same dimensions"
            )

        return sum(
            a * b
            for a, b in zip(first, second)
        )