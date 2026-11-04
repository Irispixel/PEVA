from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parents[2]

BACKEND_DIR = BASE_DIR / "backend"
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"

DATABASE_DIR = DATA_DIR / "database"
CONVERSATIONS_DIR = DATA_DIR / "conversations"
MEMORY_DIR = DATA_DIR / "memory"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"
GENERATED_IMAGES_DIR = DATA_DIR / "generated_images"
LOGS_DIR = DATA_DIR / "logs"

STT_MODELS_DIR = MODELS_DIR / "stt"
TTS_MODELS_DIR = MODELS_DIR / "tts"
WAKE_WORD_MODELS_DIR = MODELS_DIR / "wake_word"
VISION_MODELS_DIR = MODELS_DIR / "vision"


PEVA_NAME = "PEVA"
WAKE_WORD = "PEVA"

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://localhost:11434"
)

LLM_MODEL = os.getenv(
    "PEVA_LLM_MODEL",
    "qwen3.5:9b"
)


def create_directories():
    directories = [
        DATA_DIR,
        DATABASE_DIR,
        CONVERSATIONS_DIR,
        MEMORY_DIR,
        EMBEDDINGS_DIR,
        GENERATED_IMAGES_DIR,
        LOGS_DIR,
        MODELS_DIR,
        STT_MODELS_DIR,
        TTS_MODELS_DIR,
        WAKE_WORD_MODELS_DIR,
        VISION_MODELS_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)