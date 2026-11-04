from typing import Optional


class Conversation:
    def __init__(self, max_messages: int = 20):
        if max_messages <= 0:
            raise ValueError("max_messages must be greater than 0")

        self.max_messages = max_messages
        self._messages: list[dict[str, str]] = []

    def add_message(
        self,
        role: str,
        content: str,
    ):
        if role not in {"user", "assistant", "system"}:
            raise ValueError(f"Invalid message role: {role}")

        if not content or not content.strip():
            return

        self._messages.append(
            {
                "role": role,
                "content": content.strip(),
            }
        )

        self._trim()

    def add_user_message(self, content: str):
        self.add_message("user", content)

    def add_assistant_message(self, content: str):
        self.add_message("assistant", content)

    def add_system_message(self, content: str):
        self.add_message("system", content)

    def get_messages(self) -> list[dict[str, str]]:
        return self._messages.copy()

    def get_last_message(self) -> Optional[dict[str, str]]:
        if not self._messages:
            return None

        return self._messages[-1].copy()

    def clear(self):
        self._messages.clear()

    def message_count(self) -> int:
        return len(self._messages)

    def _trim(self):
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages:]