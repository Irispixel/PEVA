import ctypes
import time
import psutil
from typing import Optional

import win32gui
import win32process

class ActiveWindow:
    def __init__(self):
        self.user32 = ctypes.windll.user32

    def get_handle(self) -> Optional[int]:
        handle = self.user32.GetForegroundWindow()

        if not handle:
            return None

        return handle

    def get_title(self) -> str:
        handle = self.get_handle()

        if not handle:
            return ""

        length = self.user32.GetWindowTextLengthW(
            handle
        )

        if length <= 0:
            return ""

        buffer = ctypes.create_unicode_buffer(
            length + 1
        )

        self.user32.GetWindowTextW(
            handle,
            buffer,
            length + 1,
        )

        return buffer.value

    def is_active(
        self,
        handle: int,
    ) -> bool:
        if not handle:
            return False

        return self.get_handle() == handle

    def activate(
        self,
        handle: int,
    ) -> bool:
        if not handle:
            return False

        if not win32gui.IsWindow(handle):
            return False

        if not win32gui.IsWindowVisible(handle):
            return False

        try:
            if win32gui.IsIconic(handle):
                win32gui.ShowWindow(
                    handle,
                    9,
                )

            current_handle = self.get_handle()

            if current_handle == handle:
                return True

            current_thread = (
                win32process.GetWindowThreadProcessId(
                    current_handle
                )[0]
                if current_handle
                else 0
            )

            target_thread = (
                win32process.GetWindowThreadProcessId(
                    handle
                )[0]
            )

            attached = False

            if (
                current_thread
                and target_thread
                and current_thread != target_thread
            ):
                attached = bool(
                    self.user32.AttachThreadInput(
                        current_thread,
                        target_thread,
                        True,
                    )
                )

            try:
                self.user32.BringWindowToTop(
                    handle
                )

                self.user32.SetActiveWindow(
                    handle
                )

                self.user32.SetForegroundWindow(
                    handle
                )

            finally:
                if attached:
                    self.user32.AttachThreadInput(
                        current_thread,
                        target_thread,
                        False,
                    )

            for _ in range(20):
                time.sleep(0.05)

                if self.get_handle() == handle:
                    return True

            return False

        except Exception:
            return False
    def get_info(self) -> dict:
        handle = self.get_handle()

        if not handle:
            return {
                "success": False,
                "handle": None,
                "title": "",
            }

        return {
            "success": True,
            "handle": handle,
            "title": self.get_title(),
        }

    def find_window(
        self,
        title_contains: str,
    ) -> Optional[int]:
        if not title_contains:
            return None

        title_contains = (
            title_contains.strip().lower()
        )

        if not title_contains:
            return None

        windows = []

        def callback(
            hwnd,
            extra,
        ):
            if not win32gui.IsWindowVisible(
                hwnd
            ):
                return True

            title = win32gui.GetWindowText(
                hwnd
            ).strip()

            if (
                title
                and title_contains in title.lower()
            ):
                windows.append(hwnd)

            return True

        win32gui.EnumWindows(
            callback,
            None,
        )

        if not windows:
            return None

        return windows[0]

    def activate_by_title(
        self,
        title_contains: str,
    ) -> dict:
        handle = self.find_window(
            title_contains
        )

        if not handle:
            return {
                "success": False,
                "handle": None,
                "title": "",
                "message": (
                    "Window not found."
                ),
            }

        title = win32gui.GetWindowText(
            handle
        )

        activated = self.activate(
            handle
        )

        actual_handle = self.get_handle()

        if activated:
            return {
                "success": True,
                "handle": handle,
                "title": title,
                "active_handle": actual_handle,
                "message": (
                    "Window activated successfully."
                ),
            }

        return {
            "success": False,
            "handle": handle,
            "title": title,
            "active_handle": actual_handle,
            "message": (
                "Window was found but could "
                "not be activated."
            ),
        }
    def activate_and_verify(
        self,
        handle: int,
        timeout: float = 2.0,
    ) -> dict:
        if not handle:
            return {
                "success": False,
                "message": "Invalid window handle.",
            }

        if not win32gui.IsWindow(handle):
            return {
                "success": False,
                "message": "Window no longer exists.",
            }

        title = win32gui.GetWindowText(handle)

        if win32gui.IsIconic(handle):
            win32gui.ShowWindow(handle, 9)

        current = self.get_handle()

        if current == handle:
            return {
                "success": True,
                "handle": handle,
                "title": title,
                "message": "Window is already active.",
            }

        self.activate(handle)

        end_time = time.time() + timeout

        while time.time() < end_time:
            current = self.get_handle()

            if current == handle:
                return {
                    "success": True,
                    "handle": handle,
                    "title": title,
                    "message": "Window activated successfully.",
                }

            time.sleep(0.05)

        return {
            "success": False,
            "handle": handle,
            "title": title,
            "active_handle": self.get_handle(),
            "message": "Window was found but could not be activated.",
        }
    def find_window_by_process(
        self,
        process_name: str,
    ) -> Optional[int]:
        if not process_name:
            return None

        process_name = process_name.strip().lower()

        if not process_name.endswith(".exe"):
            process_name += ".exe"

        try:
            target_pids = {
                process.info["pid"]
                for process in psutil.process_iter(
                    ["pid", "name"]
                )
                if process.info["name"]
                and process.info["name"].strip().lower()
                == process_name
            }
        except Exception:
            return None

        if not target_pids:
            return None

        windows = []

        def callback(hwnd, extra):
            if not win32gui.IsWindowVisible(hwnd):
                return True

            try:
                _, pid = win32process.GetWindowThreadProcessId(
                    hwnd
                )
            except Exception:
                return True

            if pid not in target_pids:
                return True

            title = win32gui.GetWindowText(hwnd).strip()

            if title:
                windows.append(hwnd)

            return True

        win32gui.EnumWindows(
            callback,
            None,
        )

        return windows[0] if windows else None
    def activate_by_process(
        self,
        process_name: str,
    ) -> dict:
        handle = self.find_window_by_process(
            process_name
        )

        if not handle:
            return {
                "success": False,
                "handle": None,
                "title": "",
                "message": "Process window not found.",
            }

        activated = self.activate(handle)

        return {
            "success": activated,
            "handle": handle,
            "title": win32gui.GetWindowText(handle),
            "message": (
                "Window activated."
                if activated
                else "Failed to activate window."
            ),
        }