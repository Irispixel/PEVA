from typing import Optional

from .assistant import PEVA
from .events import Event, EventType


class Orchestrator:
    def __init__(self, peva: PEVA):
        self.peva = peva
        self._register_handlers()

    def _register_handlers(self):
        self.peva.register_handler(
            EventType.WAKE_WORD_DETECTED,
            self._handle_wake_word
        )

        self.peva.register_handler(
            EventType.WAKE_REQUESTED,
            self._handle_wake
        )

        self.peva.register_handler(
            EventType.SLEEP_REQUESTED,
            self._handle_sleep
        )

        self.peva.register_handler(
            EventType.USER_SPEECH_RECEIVED,
            self._handle_speech
        )

        self.peva.register_handler(
            EventType.CHAT_OPEN_REQUESTED,
            self._handle_chat_open
        )

        self.peva.register_handler(
            EventType.CHAT_CLOSE_REQUESTED,
            self._handle_chat_close
        )

        self.peva.register_handler(
            EventType.ERROR,
            self._handle_error
        )

    def process_event(self, event: Event):
        self.peva.emit(event)

    def _handle_wake_word(self, event: Event):
        self.peva.wake()

    def _handle_wake(self, event: Event):
        pass

    def _handle_sleep(self, event: Event):
        pass

    def _handle_speech(self, event: Event):
        if not event.data:
            return

        self.peva.start_processing()

    def _handle_chat_open(self, event: Event):
        pass

    def _handle_chat_close(self, event: Event):
        pass

    def _handle_error(self, event: Event):
        error: Optional[str] = event.data

        if error:
            print(f"PEVA Error: {error}")