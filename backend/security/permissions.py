from typing import Iterable


class PermissionManager:
    def __init__(self):
        self._allowed_tools: set[str] = set()

    def allow(self, tool_name: str):
        if not tool_name or not tool_name.strip():
            raise ValueError(
                "Tool name cannot be empty"
            )

        self._allowed_tools.add(
            tool_name.strip()
        )

    def deny(self, tool_name: str):
        self._allowed_tools.discard(
            tool_name
        )

    def allow_many(
        self,
        tool_names: Iterable[str],
    ):
        for tool_name in tool_names:
            self.allow(tool_name)

    def is_allowed(
        self,
        tool_name: str,
    ) -> bool:
        return tool_name in self._allowed_tools

    def list_allowed(self) -> list[str]:
        return sorted(
            self._allowed_tools
        )

    def clear(self):
        self._allowed_tools.clear()
