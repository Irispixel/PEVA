from typing import Any

from .manager import ApplicationManager


class ApplicationController:
    def __init__(
        self,
        manager: ApplicationManager | None = None,
    ):
        self.manager = (
            manager
            if manager is not None
            else ApplicationManager()
        )

    def open_application(
        self,
        application: str,
    ) -> dict[str, Any]:
        if not application or not application.strip():
            raise ValueError(
                "Application name cannot be empty"
            )

        return self.manager.launch(
            application.strip()
        )

    def is_application_running(
        self,
        application: str,
    ) -> bool:
        if not application or not application.strip():
            return False

        return self.manager.is_running(
            application.strip()
        )

    def available_applications(
        self,
    ) -> list[str]:
        return self.manager.list_applications()
    def close_application(
        self,
        application: str,
    ) -> dict[str, Any]:
        if not application or not application.strip():
            raise ValueError(
                "Application name cannot be empty"
            )

        return self.manager.close(
            application.strip()
        )
