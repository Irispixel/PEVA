from enum import Enum
from threading import Lock


class PEVAState(Enum):
    SLEEPING = "sleeping"
    AWAKE = "awake"
    LISTENING = "listening"
    PROCESSING = "processing"
    SPEAKING = "speaking"


class RuntimeState:
    def __init__(self):
        self._state = PEVAState.SLEEPING
        self._chat_open = False
        self._lock = Lock()

    @property
    def state(self):
        with self._lock:
            return self._state

    @property
    def chat_open(self):
        with self._lock:
            return self._chat_open

    def set_state(self, state: PEVAState):
        if not isinstance(state, PEVAState):
            raise ValueError("Invalid PEVA state")

        with self._lock:
            self._state = state

    def open_chat(self):
        with self._lock:
            self._chat_open = True

    def close_chat(self):
        with self._lock:
            self._chat_open = False

    def is_sleeping(self):
        return self.state == PEVAState.SLEEPING

    def is_awake(self):
        return self.state != PEVAState.SLEEPING

    def is_listening(self):
        return self.state == PEVAState.LISTENING

    def is_processing(self):
        return self.state == PEVAState.PROCESSING

    def is_speaking(self):
        return self.state == PEVAState.SPEAKING