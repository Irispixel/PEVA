from pathlib import Path

from faster_whisper import WhisperModel


class SpeechToText:
    def __init__(
        self,
        model_size: str = "small",
        model_dir: str | Path = "models/stt",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.model_dir = Path(model_dir)
        self.device = device
        self.compute_type = compute_type

        self.model_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.model = WhisperModel(
            model_size,
            device=device,
            compute_type=compute_type,
            download_root=str(self.model_dir),
        )

    def transcribe(
        self,
        audio_path: str | Path,
        language: str | None = None,
    ) -> dict:
        audio_path = Path(audio_path)

        if not audio_path.exists():
            return {
                "success": False,
                "text": "",
                "language": None,
                "confidence": 0.0,
                "message": f"Audio file not found: {audio_path}",
            }

        try:
            segments, info = self.model.transcribe(
                str(audio_path),
                language=language,
                beam_size=5,
                vad_filter=True,
                task="transcribe",
            )

            text_parts = []

            for segment in segments:
                text = segment.text.strip()

                if text:
                    text_parts.append(text)

            text = " ".join(text_parts).strip()

            return {
                "success": True,
                "text": text,
                "language": info.language,
                "confidence": float(
                    info.language_probability
                ),
            }

        except Exception as error:
            return {
                "success": False,
                "text": "",
                "language": None,
                "confidence": 0.0,
                "message": str(error),
            }