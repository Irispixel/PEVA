from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
from uuid import uuid4
import json

from backend.core.config import MEMORY_DIR


@dataclass
class SemanticMemory:
    id: str
    content: str
    category: str
    created_at: str
    updated_at: str


class SemanticMemoryStore:
    def __init__(
        self,
        file_path: Optional[Path] = None,
    ):
        self.file_path = file_path or (
            MEMORY_DIR / "semantic_memory.json"
        )

        self._memories: dict[str, SemanticMemory] = {}

        self._load()

    def _load(self):
        if not self.file_path.exists():
            return

        try:
            with self.file_path.open(
                "r",
                encoding="utf-8",
            ) as file:
                data = json.load(file)

            if not isinstance(data, list):
                return

            for item in data:
                if not isinstance(item, dict):
                    continue

                try:
                    memory = SemanticMemory(
                        id=item["id"],
                        content=item["content"],
                        category=item["category"],
                        created_at=item["created_at"],
                        updated_at=item["updated_at"],
                    )

                    self._memories[memory.id] = memory

                except KeyError:
                    continue

        except (
            json.JSONDecodeError,
            OSError,
        ):
            self._memories = {}

    def _save(self):
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_file = self.file_path.with_suffix(
            ".tmp"
        )

        data = [
            asdict(memory)
            for memory in self._memories.values()
        ]

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_file.replace(
            self.file_path
        )

    def add(
        self,
        content: str,
        category: str = "general",
    ) -> SemanticMemory:
        if not content or not content.strip():
            raise ValueError(
                "Memory content cannot be empty"
            )

        now = datetime.now().isoformat()

        memory = SemanticMemory(
            id=str(uuid4()),
            content=content.strip(),
            category=category.strip() or "general",
            created_at=now,
            updated_at=now,
        )

        self._memories[memory.id] = memory

        self._save()

        return memory

    def get(
        self,
        memory_id: str,
    ) -> Optional[SemanticMemory]:
        return self._memories.get(memory_id)

    def update(
        self,
        memory_id: str,
        content: str,
        category: Optional[str] = None,
    ) -> Optional[SemanticMemory]:
        memory = self._memories.get(memory_id)

        if memory is None:
            return None

        if not content or not content.strip():
            raise ValueError(
                "Memory content cannot be empty"
            )

        memory.content = content.strip()

        if category is not None:
            memory.category = (
                category.strip() or "general"
            )

        memory.updated_at = (
            datetime.now().isoformat()
        )

        self._save()

        return memory

    def delete(
        self,
        memory_id: str,
    ) -> bool:
        if memory_id not in self._memories:
            return False

        del self._memories[memory_id]

        self._save()

        return True

    def get_all(self) -> list[SemanticMemory]:
        return list(
            self._memories.values()
        )

    def search(
        self,
        query: str,
        category: Optional[str] = None,
    ) -> list[SemanticMemory]:
        if not query or not query.strip():
            return []

        query_words = set(
            query.lower().split()
        )

        results = []

        for memory in self._memories.values():
            if (
                category
                and memory.category != category
            ):
                continue

            content_words = set(
                memory.content.lower().split()
            )

            if query_words.intersection(
                content_words
            ):
                results.append(memory)

        return results

    def count(self) -> int:
        return len(self._memories)

    def export(self) -> list[dict]:
        return [
            asdict(memory)
            for memory in self._memories.values()
        ]