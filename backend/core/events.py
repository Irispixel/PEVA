from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from typing import Any


class EventType(Enum):
    WAKE_WORD_DETECTED = "wake_word_detected"
    SLEEP_REQUESTED = "sleep_requested"
    WAKE_REQUESTED = "wake_requested"

    USER_SPEECH_STARTED = "user_speech_started"
    USER_SPEECH_RECEIVED = "user_speech_received"

    THINKING_STARTED = "thinking_started"
    RESPONSE_READY = "response_ready"

    SPEAKING_STARTED = "speaking_started"
    SPEAKING_FINISHED = "speaking_finished"

    CHAT_OPEN_REQUESTED = "chat_open_requested"
    CHAT_CLOSE_REQUESTED = "chat_close_requested"

    TOOL_CALL_REQUESTED = "tool_call_requested"
    TOOL_EXECUTION_FINISHED = "tool_execution_finished"

    MEMORY_UPDATED = "memory_updated"

    ERROR = "error"


@dataclass
class Event:
    type: EventType
    data: Any = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()