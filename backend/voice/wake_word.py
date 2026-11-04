class WakeWordController:
    def __init__(
        self,
        wake_word: str = "PEVA",
    ):
        self.wake_word = wake_word.strip().lower()
        self._awake = False

    def is_awake(self) -> bool:
        return self._awake

    def wake(self) -> None:
        self._awake = True

    def sleep(self) -> None:
        self._awake = False

    def contains_wake_word(
        self,
        text: str,
    ) -> bool:
        if not text:
            return False

        return (
            self.wake_word
            in text.strip().lower()
        )

    def is_sleep_command(
        self,
        text: str,
    ) -> bool:
        if not text:
            return False

        command = text.strip().lower()

        sleep_commands = {
            "go to sleep",
            "sleep",
            "peva go to sleep",
            "peva sleep",
            "stop listening",
            "stop listening peva",
        }

        return command in sleep_commands

    def process_text(
        self,
        text: str,
    ) -> dict:
        if not text or not text.strip():
            return {
                "action": "none",
                "awake": self._awake,
            }

        if self.is_sleep_command(text):
            self.sleep()

            return {
                "action": "sleep",
                "awake": False,
                "text": text,
            }

        if self.contains_wake_word(text):
            self.wake()

            return {
                "action": "wake",
                "awake": True,
                "text": text,
            }

        return {
            "action": "command"
            if self._awake
            else "ignored",
            "awake": self._awake,
            "text": text,
        }
import numpy as np
import openwakeword
from openwakeword.model import Model


class WakeWordDetector:
    def __init__(
        self,
        threshold: float = 0.5,
    ):
        openwakeword.utils.download_models()

        self.threshold = threshold

        self.model = Model(
            inference_framework="onnx",
        )

    def detect(
        self,
        audio: bytes,
    ) -> dict:
        if not audio:
            return {
                "detected": False,
                "score": 0.0,
            }

        audio_array = np.frombuffer(
            audio,
            dtype=np.int16,
        )

        predictions = self.model.predict(
            audio_array
        )

        if not predictions:
            return {
                "detected": False,
                "score": 0.0,
            }

        best_name = max(
            predictions,
            key=predictions.get,
        )

        score = float(
            predictions[best_name]
        )

        return {
            "detected": score >= self.threshold,
            "score": score,
            "model": best_name,
        }

    def reset(self) -> None:
        self.model.reset()