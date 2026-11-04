from typing import Any

from backend.tools.registry import ToolRegistry


class ToolRouter:
    def __init__(
        self,
        registry: ToolRegistry | None = None,
    ):
        self.registry = registry or ToolRegistry()

    def register(
        self,
        name: str,
        description: str,
        handler,
        parameters: dict[str, Any] | None = None,
        risk_level: str = "low",
        allowed: bool = False,
    ):
        self.registry.register(
            name=name,
            description=description,
            handler=handler,
            parameters=parameters,
            risk_level=risk_level,
            allowed=allowed,
        )

    def unregister(
        self,
        name: str,
    ):
        self.registry.unregister(name)

    def has_tool(
        self,
        name: str,
    ) -> bool:
        return self.registry.exists(name)

    def get_tool(
        self,
        name: str,
    ):
        tool = self.registry.get(name)

        if tool is None:
            raise KeyError(
                f"Tool '{name}' is not registered"
            )

        return tool

    def list_tools(self) -> list[dict[str, Any]]:
        return self.registry.list_tools()

    def allow(
        self,
        name: str,
    ):
        self.registry.allow(name)

    def deny(
        self,
        name: str,
    ):
        self.registry.deny(name)

    def execute(
        self,
        name: str,
        arguments: dict[str, Any] | None = None,
    ) -> Any:
        if arguments is None:
            arguments = {}

        return self.registry.execute(
            name,
            **arguments,
        )