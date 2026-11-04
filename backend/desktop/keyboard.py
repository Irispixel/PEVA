from typing import Any

import pyautogui


class KeyboardController:
    def __init__(
        self,
        interval: float = 0.02,
    ):
        self.interval = interval

        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.05

    def press(
        self,
        key: str,
    ) -> dict[str, Any]:
        if not key or not key.strip():
            raise ValueError(
                "Key cannot be empty"
            )

        key = key.strip().lower()

        pyautogui.press(key)

        return {
            "success": True,
            "action": "press",
            "key": key,
        }

    def type_text(
        self,
        text: str,
    ) -> dict[str, Any]:
        if text is None:
            raise ValueError(
                "Text cannot be None"
            )

        pyautogui.write(
            text,
            interval=self.interval,
        )

        return {
            "success": True,
            "action": "type",
            "text": text,
        }

    def hotkey(
        self,
        *keys: str,
    ) -> dict[str, Any]:
        if not keys:
            raise ValueError(
                "At least one key is required"
            )

        normalized = [
            key.strip().lower()
            for key in keys
            if key and key.strip()
        ]

        if not normalized:
            raise ValueError(
                "Keys cannot be empty"
            )

        pyautogui.hotkey(
            *normalized
        )

        return {
            "success": True,
            "action": "hotkey",
            "keys": normalized,
        }

    def key_down(
        self,
        key: str,
    ) -> dict[str, Any]:
        if not key or not key.strip():
            raise ValueError(
                "Key cannot be empty"
            )

        key = key.strip().lower()

        pyautogui.keyDown(key)

        return {
            "success": True,
            "action": "key_down",
            "key": key,
        }

    def key_up(
        self,
        key: str,
    ) -> dict[str, Any]:
        if not key or not key.strip():
            raise ValueError(
                "Key cannot be empty"
            )

        key = key.strip().lower()

        pyautogui.keyUp(key)

        return {
            "success": True,
            "action": "key_up",
            "key": key,
        }