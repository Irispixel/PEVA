from typing import Any

import pyttsx3


class TextToSpeech:
    def __init__(
        self,
        rate: int = 175,
        volume: float = 1.0,
        voice_name: str = "Microsoft Zira",
    ):
        self.engine = pyttsx3.init()

        self.engine.setProperty(
            "rate",
            rate,
        )

        self.engine.setProperty(
            "volume",
            volume,
        )

        self.voice_id = self._find_voice(
            voice_name
        )

        if self.voice_id:
            self.engine.setProperty(
                "voice",
                self.voice_id,
            )

    def _find_voice(
        self,
        voice_name: str,
    ) -> str | None:
        voices = self.engine.getProperty(
            "voices"
        )

        target = voice_name.lower()

        for voice in voices:
            name = getattr(
                voice,
                "name",
                "",
            )

            if target in name.lower():
                return voice.id

        return None

    def list_voices(
        self,
    ) -> list[dict[str, Any]]:
        voices = self.engine.getProperty(
            "voices"
        )

        return [
            {
                "id": voice.id,
                "name": getattr(
                    voice,
                    "name",
                    "",
                ),
                "languages": getattr(
                    voice,
                    "languages",
                    [],
                ),
            }
            for voice in voices
        ]

    def speak(
        self,
        text: str,
    ) -> dict[str, Any]:
        if not text or not text.strip():
            return {
                "success": False,
                "message": "Text cannot be empty.",
            }

        try:
            self.engine.say(
                text.strip()
            )

            self.engine.runAndWait()

            return {
                "success": True,
                "text": text,
            }

        except Exception as error:
            return {
                "success": False,
                "text": text,
                "message": str(error),
            }

    def stop(self) -> dict[str, Any]:
        try:
            self.engine.stop()

            return {
                "success": True,
                "message": "Speech stopped.",
            }

        except Exception as error:
            return {
                "success": False,
                "message": str(error),
            }