import json
from pathlib import Path
from threading import Lock
from typing import Any, Optional

from backend.core.config import MEMORY_DIR


class LongTermMemory:
    def __init__(
        self,
        file_path: Optional[Path] = None,
    ):
        self.file_path = file_path or (
            MEMORY_DIR / "long_term_memory.json"
        )

        self._lock = Lock()
        self._memory: dict[str, Any] = {}

        self._load()

    def _load(self):
        with self._lock:
            if not self.file_path.exists():
                self._memory = {}
                return

            try:
                with self.file_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    data = json.load(file)

                if isinstance(data, dict):
                    self._memory = data
                else:
                    self._memory = {}

            except (json.JSONDecodeError, OSError):
                self._memory = {}

    def _save(self):
        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary_file = self.file_path.with_suffix(
            ".tmp"
        )

        with temporary_file.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                self._memory,
                file,
                indent=4,
                ensure_ascii=False,
            )

        temporary_file.replace(self.file_path)

    def set(
        self,
        key: str,
        value: Any,
    ):
        if not key or not key.strip():
            raise ValueError("Memory key cannot be empty")

        with self._lock:
            self._memory[key.strip()] = value
            self._save()

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:
        with self._lock:
            return self._memory.get(
                key,
                default,
            )

    def delete(self, key: str) -> bool:
        with self._lock:
            if key not in self._memory:
                return False

            del self._memory[key]
            self._save()

            return True

    def exists(self, key: str) -> bool:
        with self._lock:
            return key in self._memory

    def get_all(self) -> dict[str, Any]:
        with self._lock:
            return self._memory.copy()

    def clear(self):
        with self._lock:
            self._memory.clear()
            self._save()