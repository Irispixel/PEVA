from typing import Any

from backend.desktop.active_window import ActiveWindow
from backend.desktop.keyboard import KeyboardController


class DesktopManager:
    def __init__(self):
        self.active_window = ActiveWindow()
        self.keyboard = KeyboardController()

    def activate_window(
        self,
        title_contains: str,
    ) -> dict[str, Any]:
        handle = self.active_window.find_window(
            title_contains
        )

        if not handle:
            return {
                "success": False,
                "message": "Window not found.",
                "title": "",
                "handle": None,
            }

        result = self.active_window.activate_and_verify(
            handle
        )

        return result

    def type_in_window(
        self,
        title_contains: str,
        text: str,
    ) -> dict[str, Any]:
        activation = self.activate_window(
            title_contains
        )

        if not activation.get("success"):
            return {
                "success": False,
                "action": "type",
                "message": (
                    "Target window could not be activated."
                ),
                "activation": activation,
            }

        result = self.keyboard.type_text(
            text
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "action": "type",
            "window": activation.get(
                "title",
                "",
            ),
            "result": result,
        }

    def press_in_window(
        self,
        title_contains: str,
        key: str,
    ) -> dict[str, Any]:
        activation = self.activate_window(
            title_contains
        )

        if not activation.get("success"):
            return {
                "success": False,
                "action": "press",
                "message": (
                    "Target window could not be activated."
                ),
                "activation": activation,
            }

        result = self.keyboard.press(
            key
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "action": "press",
            "window": activation.get(
                "title",
                "",
            ),
            "result": result,
        }

    def hotkey_in_window(
        self,
        title_contains: str,
        keys: list[str],
    ) -> dict[str, Any]:
        activation = self.activate_window(
            title_contains
        )

        if not activation.get("success"):
            return {
                "success": False,
                "action": "hotkey",
                "message": (
                    "Target window could not be activated."
                ),
                "activation": activation,
            }

        result = self.keyboard.hotkey(
            *keys
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "action": "hotkey",
            "window": activation.get(
                "title",
                "",
            ),
            "result": result,
        }
    def select_all_in_window(
        self,
        title_contains: str,
    ) -> dict[str, Any]:
        activation = self.activate_window(
            title_contains
        )

        if not activation.get("success"):
            return {
                "success": False,
                "action": "select_all",
                "message": (
                    "Target window could not be activated."
                ),
                "activation": activation,
            }

        result = self.keyboard.hotkey(
            "ctrl",
            "a",
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "action": "select_all",
            "window": activation.get(
                "title",
                "",
            ),
            "result": result,
        }
    def activate_process(
        self,
        process_name: str,
    ) -> dict[str, Any]:
        handle = self.active_window.find_window_by_process(
            process_name
        )

        if not handle:
            return {
                "success": False,
                "handle": None,
                "title": "",
               "message": "Application window not found.",
            }

        return self.active_window.activate_and_verify(
            handle
        )
    def type_in_process(
        self,
        process_name: str,
        text: str,
    ) -> dict[str, Any]:
        activation = self.activate_process(
            process_name
        )

        if not activation.get("success"):
            return {
                "success": False,
                "action": "type",
                "message": (
                    "Application could not be activated."
                ),
                "activation": activation,
            }

        result = self.keyboard.type_text(
            text
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "action": "type",
            "application": process_name,
            "window": activation.get(
                "title",
                "",
            ),
            "result": result,
        }
    def select_all_in_process(
        self,
        process_name: str,
    ) -> dict[str, Any]:
        activation = self.activate_process(
            process_name
        )

        if not activation.get("success"):
            return {
                "success": False,
                "action": "select_all",
                "message": (
                    "Application could not be activated."
                ),
                "activation": activation,
            }

        result = self.keyboard.hotkey(
            "ctrl",
            "a",
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "action": "select_all",
            "application": process_name,
            "window": activation.get(
                "title",
                "",
            ),
            "result": result,
        }