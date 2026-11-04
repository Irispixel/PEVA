from typing import Any


class ConfirmationManager:
    def __init__(self):
        self._pending: dict[str, dict[str, Any]] = {}

    def requires_confirmation(
        self,
        tool_name: str,
        risk_level: str = "low",
    ) -> bool:
        return risk_level.lower() in {
            "high",
            "critical",
        }

    def request_confirmation(
        self,
        tool_name: str,
        parameters: dict[str, Any],
        risk_level: str = "high",
    ) -> dict[str, Any]:
        request = {
            "tool_name": tool_name,
            "parameters": parameters,
            "risk_level": risk_level,
            "confirmed": False,
        }

        self._pending[tool_name] = request

        return request

    def confirm(self, tool_name: str) -> bool:
        request = self._pending.get(tool_name)

        if request is None:
            return False

        request["confirmed"] = True
        return True

    def deny(self, tool_name: str) -> bool:
        if tool_name not in self._pending:
            return False

        del self._pending[tool_name]
        return True

    def is_confirmed(self, tool_name: str) -> bool:
        request = self._pending.get(tool_name)

        if request is None:
            return False

        return request.get("confirmed", False)

    def get_pending(
        self,
        tool_name: str,
    ) -> dict[str, Any] | None:
        return self._pending.get(tool_name)

    def clear(self, tool_name: str):
        self._pending.pop(tool_name, None)
