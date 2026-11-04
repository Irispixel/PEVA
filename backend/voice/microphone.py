from pathlib import Path
import time
import wave

import sounddevice as sd

from backend.voice.vad import VoiceActivityDetector


class Microphone:
    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device: int | str | None = 1,
    ):
        self.sample_rate = sample_rate
        self.channels = channels
        self.device = device

        self.vad = VoiceActivityDetector(
            sample_rate=sample_rate
        )

    def list_devices(self) -> list[dict]:
        devices = sd.query_devices()

        result = []

        for index, device in enumerate(devices):
            if device["max_input_channels"] > 0:
                result.append(
                    {
                        "index": index,
                        "name": device["name"],
                        "channels": device[
                            "max_input_channels"
                        ],
                        "sample_rate": device[
                            "default_samplerate"
                        ],
                    }
                )

        return result

    def get_default_device(self) -> dict:
        device = sd.query_devices(
            self.device,
            "input",
        )

        return {
            "name": device["name"],
            "channels": device[
                "max_input_channels"
            ],
            "sample_rate": device[
                "default_samplerate"
            ],
        }

    def record(
        self,
        duration: float,
        output_path: str | Path,
    ) -> dict:
        if duration <= 0:
            raise ValueError(
                "Recording duration must be greater than zero."
            )

        output_path = Path(output_path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        frames = int(
            duration * self.sample_rate
        )

        try:
            recording = sd.rec(
                frames,
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                device=self.device,
                blocking=True,
            )

            with wave.open(
                str(output_path),
                "wb",
            ) as wav:
                wav.setnchannels(
                    self.channels
                )
                wav.setsampwidth(2)
                wav.setframerate(
                    self.sample_rate
                )
                wav.writeframes(
                    recording.tobytes()
                )

            return {
                "success": True,
                "path": str(output_path),
                "duration": duration,
                "sample_rate": self.sample_rate,
                "channels": self.channels,
            }

        except Exception as error:
            return {
                "success": False,
                "path": str(output_path),
                "message": str(error),
            }

    def record_until_silence(
        self,
        output_path: str | Path,
        max_duration: float = 15.0,
        silence_duration: float = 1.2,
        start_timeout: float = 5.0,
    ) -> dict:
        output_path = Path(output_path)
        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        frame_duration = (
            self.vad.frame_duration_ms
            / 1000
        )

        frames = []

        speech_started = False
        silence_time = 0.0
        start_time = time.time()

        try:
            with sd.RawInputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                dtype="int16",
                blocksize=self.vad.frame_size,
                device=self.device,
            ) as stream:

                while True:
                    data, overflowed = (
                        stream.read(
                            self.vad.frame_size
                        )
                    )

                    if overflowed:
                        continue

                    frame = bytes(data)

                    speech = self.vad.is_speech(
                        frame
                    )

                    if speech:
                        speech_started = True
                        silence_time = 0.0
                        frames.append(frame)

                    elif speech_started:
                        frames.append(frame)
                        silence_time += (
                            frame_duration
                        )

                    if not speech_started:
                        if (
                            time.time()
                            - start_time
                            >= start_timeout
                        ):
                            return {
                                "success": False,
                                "message": (
                                    "No speech detected."
                                ),
                            }

                    if speech_started:
                        elapsed = (
                            time.time()
                            - start_time
                        )

                        if (
                            silence_time
                            >= silence_duration
                        ):
                            break

                        if (
                            elapsed
                            >= max_duration
                        ):
                            break

            audio_data = b"".join(frames)

            with wave.open(
                str(output_path),
                "wb",
            ) as wav:
                wav.setnchannels(
                    self.channels
                )
                wav.setsampwidth(2)
                wav.setframerate(
                    self.sample_rate
                )
                wav.writeframes(
                    audio_data
                )

            return {
                "success": True,
                "path": str(output_path),
                "duration": (
                    len(audio_data)
                    / (
                        self.sample_rate
                        * self.channels
                        * 2
                    )
                ),
                "sample_rate": self.sample_rate,
                "channels": self.channels,
            }

        except Exception as error:
            return {
                "success": False,
                "path": str(output_path),
                "message": str(error),
            }