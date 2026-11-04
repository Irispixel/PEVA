from typing import Any, Callable

from backend.security.command_validator import CommandValidator
from backend.security.confirmation import ConfirmationManager
from backend.security.permissions import PermissionManager


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, dict[str, Any]] = {}

        self.validator = CommandValidator()
        self.confirmation = ConfirmationManager()
        self.permissions = PermissionManager()

    def register(
        self,
        name: str,
        description: str,
        handler: Callable,
        parameters: dict[str, Any] | None = None,
        risk_level: str = "low",
        allowed: bool = False,
    ):
        if not name or not name.strip():
            raise ValueError(
                "Tool name cannot be empty"
            )

        if not callable(handler):
            raise TypeError(
                "Tool handler must be callable"
            )

        if risk_level not in {
            "low",
            "medium",
            "high",
            "critical",
        }:
            raise ValueError(
                "Invalid risk level"
            )

        name = name.strip()

        self._tools[name] = {
            "name": name,
            "description": description,
            "handler": handler,
            "parameters": parameters or {},
            "risk_level": risk_level,
        }

        if allowed:
            self.permissions.allow(name)

    def unregister(self, name: str):
        self._tools.pop(name, None)
        self.permissions.deny(name)
        self.confirmation.clear(name)

    def get(
        self,
        name: str,
    ) -> dict[str, Any] | None:
        return self._tools.get(name)

    def exists(self, name: str) -> bool:
        return name in self._tools

    def allow(self, name: str):
        if not self.exists(name):
            raise ValueError(
                f"Tool not found: {name}"
            )

        self.permissions.allow(name)

    def deny(self, name: str):
        self.permissions.deny(name)

    def list_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool["name"],
                "description": tool["description"],
                "parameters": tool["parameters"],
                "risk_level": tool["risk_level"],
                "allowed": self.permissions.is_allowed(
                    tool["name"]
                ),
            }
            for tool in self._tools.values()
        ]

    def execute(
        self,
        name: str,
        **kwargs,
    ) -> Any:
        tool = self.get(name)

        if tool is None:
            raise ValueError(
                f"Tool not found: {name}"
            )

        if not self.permissions.is_allowed(name):
            raise PermissionError(
                f"Tool is not allowed: {name}"
            )

        if not self.validator.validate(
            name,
            kwargs,
        ):
            raise PermissionError(
                f"Tool request rejected: {name}"
            )

        risk_level = tool["risk_level"]

        if self.confirmation.requires_confirmation(
            name,
            risk_level,
        ):
            if not self.confirmation.is_confirmed(name):
                return self.confirmation.request_confirmation(
                    tool_name=name,
                    parameters=kwargs,
                    risk_level=risk_level,
                )

        try:
            return tool["handler"](**kwargs)

        finally:
            if self.confirmation.is_confirmed(name):
                self.confirmation.clear(name)
