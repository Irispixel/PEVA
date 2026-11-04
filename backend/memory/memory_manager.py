from typing import Any, Optional

from backend.memory.long_term import LongTermMemory
from backend.memory.semantic import SemanticMemoryStore
from backend.memory.embeddings import EmbeddingModel
from backend.memory.retriever import (
    MemoryRetriever,
    MemoryResult,
)


class MemoryManager:
    def __init__(
        self,
        long_term: Optional[LongTermMemory] = None,
        semantic: Optional[SemanticMemoryStore] = None,
        embedding_model: Optional[EmbeddingModel] = None,
    ):
        self.long_term = (
            long_term or LongTermMemory()
        )

        self.semantic = (
            semantic or SemanticMemoryStore()
        )

        self.embedding_model = (
            embedding_model or EmbeddingModel()
        )

        self.retriever = MemoryRetriever(
            memory_store=self.semantic,
            embedding_model=self.embedding_model,
        )

    def remember(
        self,
        key: str,
        value: Any,
    ):
        self.long_term.set(
            key,
            value,
        )

    def recall(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        return self.long_term.get(
            key,
            default,
        )

    def forget(
        self,
        key: str,
    ) -> bool:
        return self.long_term.delete(key)

    def remember_semantic(
        self,
        content: str,
        category: str = "general",
    ):
        existing = self.semantic.search(
            query=content,
            category=category,
        )

        if existing:
            best_match = None
            best_score = 0.0

            new_embedding = self.embedding_model.encode(
                content
            )

            for memory in existing:
                old_embedding = self.retriever._embeddings.get(
                    memory.id
                )

                if old_embedding is None:
                    self.retriever.index_memory(memory)
                    old_embedding = self.retriever._embeddings[
                        memory.id
                    ]

                score = self.embedding_model.similarity(
                    new_embedding,
                    old_embedding,
                )

                if score > best_score:
                    best_score = score
                    best_match = memory

            if best_match and best_score >= 0.75:
                updated = self.semantic.update(
                    memory_id=best_match.id,
                    content=content,
                    category=category,
                )

                if updated:
                    self.retriever.index_memory(
                        updated
                    )

                return updated

        memory = self.semantic.add(
            content=content,
            category=category,
        )

        self.retriever.index_memory(
            memory
        )

        return memory

    def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.3,
        category: Optional[str] = None,
    ) -> list[MemoryResult]:
        return self.retriever.search(
            query=query,
            top_k=top_k,
            min_score=min_score,
            category=category,
        )

    def get_all_semantic_memories(self):
        return self.semantic.get_all()

    def delete_semantic_memory(
        self,
        memory_id: str,
    ) -> bool:
        deleted = self.semantic.delete(
            memory_id
        )

        if deleted:
            self.retriever.remove_from_index(
                memory_id
            )

        return deleted

    def clear_all(self):
        self.long_term.clear()

        for memory in self.semantic.get_all():
            self.retriever.remove_from_index(
                memory.id
            )

        for memory in list(
            self.semantic.get_all()
        ):
            self.semantic.delete(memory.id)

    def get_status(self) -> dict:
        return {
            "long_term_memories": len(
                self.long_term.get_all()
            ),
            "semantic_memories": self.semantic.count(),
            "indexed_memories": len(
                self.retriever._embeddings
            ),
        }