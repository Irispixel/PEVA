from typing import Any


class CommandValidator:
    def __init__(self):
        self._blocked_commands = {
            "format",
            "diskpart",
            "shutdown",
            "restart-computer",
            "remove-item",
            "del",
            "rd",
            "rmdir",
        }

    def validate(
        self,
        tool_name: str,
        parameters: dict[str, Any],
    ) -> bool:
        if not tool_name or not tool_name.strip():
            return False

        if not isinstance(parameters, dict):
            return False

        if self._contains_blocked_command(parameters):
            return False

        return True

    def _contains_blocked_command(
        self,
        parameters: dict[str, Any],
    ) -> bool:
        for value in parameters.values():
            if not isinstance(value, str):
                continue

            command = value.strip().lower()

            for blocked in self._blocked_commands:
                if command == blocked:
                    return True

                if command.startswith(blocked + " "):
                    return True

        return False