from dataclasses import dataclass
from typing import Optional

from backend.memory.embeddings import EmbeddingModel
from backend.memory.semantic import (
    SemanticMemory,
    SemanticMemoryStore,
)


@dataclass
class MemoryResult:
    memory: SemanticMemory
    score: float


class MemoryRetriever:
    def __init__(
        self,
        memory_store: SemanticMemoryStore,
        embedding_model: Optional[EmbeddingModel] = None,
    ):
        self.memory_store = memory_store
        self.embedding_model = (
            embedding_model or EmbeddingModel()
        )

        self._embeddings: dict[str, list[float]] = {}

    def index_memory(
        self,
        memory: SemanticMemory,
    ):
        embedding = self.embedding_model.encode(
            memory.content
        )

        self._embeddings[memory.id] = embedding

    def remove_from_index(
        self,
        memory_id: str,
    ):
        self._embeddings.pop(
            memory_id,
            None,
        )

    def rebuild_index(self):
        self._embeddings.clear()

        for memory in self.memory_store.get_all():
            self.index_memory(memory)

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.3,
        category: Optional[str] = None,
    ) -> list[MemoryResult]:
        if not query or not query.strip():
            return []

        if top_k <= 0:
            return []

        query_embedding = self.embedding_model.encode(
            query
        )

        results = []

        for memory in self.memory_store.get_all():
            if category and memory.category != category:
                continue

            memory_embedding = self._embeddings.get(
                memory.id
            )

            if memory_embedding is None:
                self.index_memory(memory)
                memory_embedding = self._embeddings[memory.id]

            score = self.embedding_model.similarity(
                query_embedding,
                memory_embedding,
            )

            if score >= min_score:
                results.append(
                    MemoryResult(
                        memory=memory,
                        score=score,
                    )
                )

        results.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return results[:top_k]