from typing import Any

from .launcher import ApplicationLauncher


class ApplicationManager:
    def __init__(self):
        self.launcher = ApplicationLauncher()

        self._applications = {
            "notepad": "notepad.exe",
            "calculator": "calc.exe",
            "paint": "mspaint.exe",
            "explorer": "explorer.exe",
            "cmd": "cmd.exe",
            "powershell": "powershell.exe",
        }

    def register_application(
        self,
        name: str,
        command: str,
    ):
        if not name or not name.strip():
            raise ValueError(
                "Application name cannot be empty"
            )

        if not command or not command.strip():
            raise ValueError(
                "Application command cannot be empty"
            )

        self._applications[
            name.strip().lower()
        ] = command.strip()

    def remove_application(
        self,
        name: str,
    ):
        self._applications.pop(
            name.strip().lower(),
            None,
        )

    def is_registered(
        self,
        name: str,
    ) -> bool:
        return (
            name.strip().lower()
            in self._applications
        )

    def list_applications(self) -> list[str]:
        return list(
            self._applications.keys()
        )

    def launch(
        self,
        name: str,
    ) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValueError(
                "Application name cannot be empty"
            )

        application = name.strip().lower()

        command = self._applications.get(
            application
        )

        if command is None:
            raise ValueError(
                f"Application is not registered: "
                f"{name}"
            )

        return self.launcher.launch(
            command=command,
            name=application,
        )

    def is_running(
        self,
        name: str,
    ) -> bool:
        return self.launcher.is_running(
            name.strip().lower()
        )

    def list_running(self) -> list[str]:
        return self.launcher.list_running()
    def close(
        self,
        name: str,
    ) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValueError(
                "Application name cannot be empty"
            )

        application = name.strip().lower()

        if not self.is_registered(application):
            raise ValueError(
                f"Application is not registered: {name}"
            )

        return self.launcher.close(
            application
        )