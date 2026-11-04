import subprocess
import time
from typing import Any


class ApplicationLauncher:
    def __init__(self):
        self._processes: dict[str, dict[str, Any]] = {}

    def _get_process_ids(
        self,
        process_name: str,
    ) -> set[int]:
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        f"Get-Process -Name '{process_name}' "
                        "-ErrorAction SilentlyContinue "
                        "| Select-Object -ExpandProperty Id"
                    ),
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode != 0:
                return set()

            process_ids = set()

            for line in result.stdout.splitlines():
                line = line.strip()

                if line.isdigit():
                    process_ids.add(int(line))

            return process_ids

        except (
            subprocess.SubprocessError,
            OSError,
        ):
            return set()

    def _find_new_process(
        self,
        process_name: str,
        previous_ids: set[int],
        timeout: float = 5.0,
    ) -> int | None:
        end_time = time.time() + timeout

        while time.time() < end_time:
            current_ids = self._get_process_ids(
                process_name
            )

            new_ids = current_ids - previous_ids

            if new_ids:
                return next(iter(new_ids))

            time.sleep(0.25)

        return None

    def launch(
        self,
        command: str,
        name: str | None = None,
    ) -> dict[str, Any]:
        if not command or not command.strip():
            raise ValueError(
                "Application command cannot be empty"
            )

        command = command.strip()

        process_name = (
            name.strip().lower()
            if name and name.strip()
            else command.lower()
        )

        executable_name = command

        if executable_name.lower().endswith(".exe"):
            executable_name = executable_name[:-4]

        previous_ids = self._get_process_ids(
            executable_name
        )

        process = subprocess.Popen(
            [command],
            shell=False,
        )

        actual_pid = self._find_new_process(
            process_name=executable_name,
            previous_ids=previous_ids,
        )

        if actual_pid is None:
            actual_pid = process.pid

        self._processes[process_name] = {
            "launcher": process,
            "pid": actual_pid,
            "command": command,
        }

        return {
            "success": True,
            "name": process_name,
            "pid": actual_pid,
            "launcher_pid": process.pid,
            "command": command,
        }

    def _process_exists(
        self,
        pid: int,
    ) -> bool:
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        f"Get-Process -Id {pid} "
                        "-ErrorAction SilentlyContinue"
                    ),
                ],
                capture_output=True,
                timeout=5,
            )

            return result.returncode == 0

        except (
            subprocess.SubprocessError,
            OSError,
        ):
            return False

    def is_running(
        self,
        name: str,
    ) -> bool:
        process_name = name.strip().lower()

        entry = self._processes.get(
            process_name
        )

        if entry is None:
            return False

        return self._process_exists(
            entry["pid"]
        )

    def close(
        self,
        name: str,
    ) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValueError(
                "Application name cannot be empty"
            )

        process_name = name.strip().lower()

        entry = self._processes.get(
            process_name
        )

        pid = None

        if entry is not None:
            pid = entry["pid"]

            if not self._process_exists(pid):
                del self._processes[process_name]

                return {
                    "success": False,
                    "name": process_name,
                    "pid": pid,
                    "message": "Application is already closed.",
                }

        else:
            process_ids = self._get_process_ids(
                process_name
            )

            if not process_ids:
                return {
                    "success": False,
                    "name": process_name,
                    "message": "Application is not running.",
                }

            pid = next(iter(process_ids))

        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-NoProfile",
                    "-Command",
                    (
                        f"$p = Get-Process -Id {pid} "
                        "-ErrorAction SilentlyContinue; "
                        "if ($p -and $p.MainWindowHandle -ne 0) { "
                        "$p.CloseMainWindow() | Out-Null; "
                        "Write-Output 'WINDOW_CLOSE_SENT' "
                        "} elseif ($p) { "
                        "Write-Output 'NO_MAIN_WINDOW' "
                        "} else { "
                        "Write-Output 'PROCESS_NOT_FOUND' "
                        "}"
                    ),
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            output = result.stdout.strip()

            if "PROCESS_NOT_FOUND" in output:
                return {
                    "success": False,
                    "name": process_name,
                    "pid": pid,
                    "message": "Application is already closed.",
                }

            if "NO_MAIN_WINDOW" in output:
                return {
                    "success": False,
                    "name": process_name,
                    "pid": pid,
                    "message": (
                        "Application is running but has "
                        "no main window."
                    ),
                }

            if "WINDOW_CLOSE_SENT" not in output:
                return {
                    "success": False,
                    "name": process_name,
                    "pid": pid,
                    "message": (
                        result.stderr.strip()
                        or "Failed to request application close."
                    ),
                }

            end_time = time.time() + 5

            while time.time() < end_time:
                if not self._process_exists(pid):
                    self._processes.pop(
                        process_name,
                        None,
                    )

                    return {
                        "success": True,
                        "name": process_name,
                        "pid": pid,
                        "message": (
                            "Application closed successfully."
                        ),
                    }

                time.sleep(0.25)

            return {
                "success": False,
                "name": process_name,
                "pid": pid,
                "message": (
                    "Close request was sent, but the "
                    "application is still running."
                ),
            }

        except (
            subprocess.SubprocessError,
            OSError,
        ) as error:
            return {
                "success": False,
                "name": process_name,
                "pid": pid,
                "message": str(error),
            }
    def list_running(self) -> list[str]:
        running = []

        for name in list(
            self._processes.keys()
        ):
            if self.is_running(name):
                running.append(name)

        return running

    def remove_finished(self):
        finished = []

        for name in self._processes:
            if not self.is_running(name):
                finished.append(name)

        for name in finished:
            self._processes.pop(
                name,
                None,
            )
