import os
import time
import wave

import pyaudio


OUTPUT_DIR = os.path.join(
    "models",
    "wake_word",
    "training",
    "negative",
)

SAMPLE_RATE = 16000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK = 1024
RECORD_SECONDS = 5


def record_sample(index: int) -> None:
    os.makedirs(
        OUTPUT_DIR,
        exist_ok=True,
    )

    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK,
    )

    print()
    print(f"Negative sample {index}")
    print("Speak naturally.")
    print("DO NOT say PEVA.")
    print("Recording...")

    frames = []

    for _ in range(
        int(
            SAMPLE_RATE
            / CHUNK
            * RECORD_SECONDS
        )
    ):
        frames.append(
            stream.read(
                CHUNK,
                exception_on_overflow=False,
            )
        )

    stream.stop_stream()
    stream.close()
    audio.terminate()

    path = os.path.join(
        OUTPUT_DIR,
        f"negative_{index:03d}.wav",
    )

    with wave.open(path, "wb") as file:
        file.setnchannels(CHANNELS)
        file.setsampwidth(2)
        file.setframerate(SAMPLE_RATE)
        file.writeframes(
            b"".join(frames)
        )

    print(f"Saved: {path}")


def main():
    print("PEVA Negative Wake Word Recorder")
    print("=================================")
    print()
    print("You will record 10 samples.")
    print("Speak naturally without saying PEVA.")
    print()

    input("Press Enter to start...")

    for index in range(1, 11):
        print()
        print("Get ready...")
        time.sleep(1)

        record_sample(index)

        time.sleep(0.5)

    print()
    print("Negative recording complete.")


if __name__ == "__main__":
    main()