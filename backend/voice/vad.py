import webrtcvad


class VoiceActivityDetector:
    def __init__(
        self,
        sample_rate: int = 16000,
        aggressiveness: int = 2,
        frame_duration_ms: int = 30,
    ):
        if sample_rate not in (8000, 16000, 32000, 48000):
            raise ValueError(
                "Unsupported sample rate."
            )

        if aggressiveness not in range(4):
            raise ValueError(
                "Aggressiveness must be between 0 and 3."
            )

        if frame_duration_ms not in (
            10,
            20,
            30,
        ):
            raise ValueError(
                "Frame duration must be 10, 20, or 30 ms."
            )

        self.sample_rate = sample_rate
        self.frame_duration_ms = frame_duration_ms

        self.vad = webrtcvad.Vad(
            aggressiveness
        )

        self.frame_size = int(
            sample_rate
            * frame_duration_ms
            / 1000
        )

    def is_speech(
        self,
        frame: bytes,
    ) -> bool:
        expected_bytes = (
            self.frame_size * 2
        )

        if len(frame) != expected_bytes:
            return False

        return self.vad.is_speech(
            frame,
            self.sample_rate,
        )

    def frame_size_bytes(self) -> int:
        return self.frame_size * 2