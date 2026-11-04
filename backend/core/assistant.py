import json
import re

from typing import Any, Callable, Dict, List

from .events import Event, EventType
from .state import PEVAState, RuntimeState

from backend.memory.conversation import Conversation
from backend.memory.memory_manager import MemoryManager

from backend.llm.ollama_client import OllamaClient
from backend.llm.tool_router import ToolRouter
from backend.tools.applications.controller import ApplicationController
from backend.desktop.keyboard import KeyboardController
from backend.desktop.desktop_manager import DesktopManager
from backend.voice.microphone import Microphone
from backend.voice.stt import SpeechToText
from backend.voice.tts import TextToSpeech

class PEVA:
    def __init__(self):
        self.runtime = RuntimeState()
        self.memory = MemoryManager()
        self.conversation = Conversation()
        self.llm = OllamaClient()
        self.tools = ToolRouter()
        self.application_controller = ApplicationController()
        self.keyboard_controller = KeyboardController()
        self.desktop = DesktopManager()

        self._handlers: Dict[EventType, List[Callable[[Event], None]]] = {}
        self.microphone = Microphone(
                                device=1
                            )
        self.stt = SpeechToText()
        self.tts = TextToSpeech()

        self._register_keyboard_tools()
        self._register_application_tools()
        self._register_desktop_tools()
    def _register_keyboard_tools(self):
        if not self.tools.has_tool("keyboard_type"):
            self.tools.register(
                name="keyboard_type",
                description=(
                    "Type text using the keyboard into "
                    "the currently focused application."
                ),
                handler=self.keyboard_controller.type_text,
                parameters={
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": (
                                "Text that should be typed."
                            ),
                        }
                    },
                    "required": [
                        "text"
                    ],
                },
                risk_level="medium",
                allowed=True,
            )

        if not self.tools.has_tool("keyboard_press"):
            self.tools.register(
                name="keyboard_press",
                description=(
                    "Press a single keyboard key in "
                    "the currently focused application."
                ),
                handler=self.keyboard_controller.press,
                parameters={
                    "type": "object",
                    "properties": {
                        "key": {
                            "type": "string",
                            "description": (
                                "Keyboard key such as enter, "
                                "esc, tab, space, or backspace."
                            ),
                        }
                    },
                    "required": [
                        "key"
                    ],
                },
                risk_level="medium",
                allowed=True,
            )

        if not self.tools.has_tool("keyboard_hotkey"):
            self.tools.register(
                name="keyboard_hotkey",
                description=(
                    "Press a keyboard shortcut such as "
                    "ctrl+c, ctrl+v, ctrl+a, or alt+tab."
                ),
                handler=self._keyboard_hotkey,
                parameters={
                    "type": "object",
                    "properties": {
                        "keys": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": (
                                "Keys that should be pressed "
                                "together."
                            ),
                        }
                    },
                    "required": [
                        "keys"
                    ],
                },
                risk_level="medium",
                allowed=True,
            )
    def _register_application_tools(self):
        if not self.tools.has_tool("open_application"):
            self.tools.register(
                name="open_application",
                description=(
                    "Open a registered Windows application. "
                    "Only applications registered by PEVA are allowed."
                ),
                handler=self.application_controller.open_application,
                parameters={
                    "type": "object",
                    "properties": {
                        "application": {
                            "type": "string",
                            "description": (
                                "Name of the registered application "
                                "to open, such as notepad, calculator, "
                                "paint, or explorer."
                            ),
                        }
                    },
                    "required": [
                        "application"
                    ],
                },
                risk_level="medium",
                allowed=True,
            )

        if not self.tools.has_tool("close_application"):
            self.tools.register(
                name="close_application",
                description=(
                    "Close a Windows application that was "
                    "previously launched and is being tracked by PEVA."
                ),
                handler=self.application_controller.close_application,
                parameters={
                    "type": "object",
                    "properties": {
                        "application": {
                            "type": "string",
                            "description": (
                                "Name of the application to close, "
                                "such as notepad, calculator, "
                                "paint, or explorer."
                            ),
                        }
                    },
                    "required": [
                        "application"
                    ],
                },
                risk_level="medium",
                allowed=True,
            )
    def _register_desktop_tools(self):
        if not self.tools.has_tool("select_all_in_window"):
            self.tools.register(
                name="select_all_in_window",
                description=(
                    "Select all text inside a Windows application. "
                    "Use this when the user asks to select all text "
                    "in an application such as Notepad, Paint, or VS Code."
                ),
                handler=self.desktop.select_all_in_process,
                parameters={
                    "type": "object",
                    "properties": {
                        "process_name": {
                            "type": "string",
                            "description": (
                                "The application process name. "
                                "Examples: Notepad, notepad.exe, "
                                "Code, code.exe."
                            ),
                        }
                    },
                    "required": [
                        "process_name"
                    ],
                },
                risk_level="medium",
                allowed=True,
            )

        if not self.tools.has_tool("type_in_window"):
            self.tools.register(
               name="type_in_window",
                description=(
                    "Activate a running Windows application and "
                    "type text into it."
                ),
                handler=self.desktop.type_in_process,
                parameters={
                    "type": "object",
                    "properties": {
                        "process_name": {
                            "type": "string",
                            "description": (
                                "Windows process name, such as "
                                "Notepad.exe or Code.exe."
                            ),
                        },
                        "text": {
                            "type": "string",
                            "description": (
                                "Text to type into the application."
                            ),
                        },
                    },
                    "required": [
                        "process_name",
                        "text",
                    ],
                },
                risk_level="medium",
                allowed=True,
            )
    def register_handler(
        self,
        event_type: EventType,
        handler: Callable[[Event], None],
    ):
        if event_type not in self._handlers:
            self._handlers[event_type] = []

        self._handlers[event_type].append(handler)
    def emit(self, event: Event):
        handlers = self._handlers.get(event.type, [])

        for handler in handlers:
            handler(event)

    def wake(self) -> str:
        self.runtime.set_state(
            PEVAState.AWAKE
        )

        greeting = self.get_personalized_greeting()

        self.emit(
            Event(
                type=EventType.WAKE_REQUESTED,
                data=greeting,
            )
        )

        return greeting
    def _keyboard_hotkey(
        self,
        keys: list[str],
    ):
        if not isinstance(keys, list):
            raise ValueError(
                "keys must be a list"
            )

        if not keys:
            raise ValueError(
                "At least one key is required"
            )

        return self.keyboard_controller.hotkey(
            *keys
        )
    def sleep(self) -> str:
        goodbye = self.get_personalized_goodbye()

        self.emit(
            Event(
                type=EventType.SLEEP_REQUESTED,
                data=goodbye,
            )
        )

        self.runtime.set_state(
            PEVAState.SLEEPING
        )

        return goodbye

    def start_listening(self):
        if self.runtime.is_sleeping():
            return

        self.runtime.set_state(
            PEVAState.LISTENING
        )

        self.emit(
            Event(
                type=EventType.USER_SPEECH_STARTED
            )
        )

    def start_processing(self):
        self.runtime.set_state(
            PEVAState.PROCESSING
        )

        self.emit(
            Event(
                type=EventType.THINKING_STARTED
            )
        )

    def start_speaking(self):
        self.runtime.set_state(
            PEVAState.SPEAKING
        )

        self.emit(
            Event(
                type=EventType.SPEAKING_STARTED
            )
        )

    def finish_speaking(self):
        self.runtime.set_state(
            PEVAState.AWAKE
        )

        self.emit(
            Event(
                type=EventType.SPEAKING_FINISHED
            )
        )

    def open_chat(self):
        self.runtime.open_chat()

        self.emit(
            Event(
                type=EventType.CHAT_OPEN_REQUESTED
            )
        )

    def close_chat(self):
        self.runtime.close_chat()

        self.emit(
            Event(
                type=EventType.CHAT_CLOSE_REQUESTED
            )
        )

    def register_tool(
        self,
        name: str,
        description: str,
        handler,
        parameters: dict[str, Any] | None = None,
        risk_level: str = "low",
        allowed: bool = False,
    ):
        self.tools.register(
            name=name,
            description=description,
            handler=handler,
            parameters=parameters,
            risk_level=risk_level,
            allowed=allowed,
        )

    def allow_tool(
        self,
        name: str,
    ):
        self.tools.allow(name)

    def deny_tool(
        self,
        name: str,
    ):
        self.tools.deny(name)

    def list_tools(self):
        return self.tools.list_tools()

    def _build_tool_definitions(self) -> list[dict]:
        definitions = []

        for tool in self.tools.list_tools():
            parameters = tool.get(
                "parameters",
                {},
            )

            if (
                not isinstance(parameters, dict)
                or parameters.get("type") != "object"
            ):
                parameters = {
                    "type": "object",
                    "properties": parameters,
                    "required": list(
                        parameters.keys()
                    ),
                }

            definitions.append(
                {
                    "type": "function",
                    "function": {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": parameters,
                    },
                }
            )

        return definitions
    def _execute_tool_calls(
        self,
        tool_calls: list[dict],
    ) -> list[dict]:
        results = []

        for tool_call in tool_calls:
            function = tool_call.get(
                "function",
                {},
            )

            name = function.get(
                "name",
                "",
            )

            arguments = function.get(
                "arguments",
                {},
            )

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            if not isinstance(arguments, dict):
                arguments = {}

            print(
                "\n[TOOL CALL]"
            )
            print(
                "NAME:",
                name,
            )
            print(
                "ARGUMENTS:",
                arguments,
            )

            self.emit(
                Event(
                    type=EventType.TOOL_CALL_REQUESTED,
                    data=tool_call,
                )
            )

            try:
                result = self.tools.execute(
                    name,
                    arguments,
                )

                print(
                    "[TOOL RESULT]:",
                    result,
                )

                self.emit(
                    Event(
                        type=EventType.TOOL_EXECUTION_FINISHED,
                        data={
                            "tool": name,
                            "arguments": arguments,
                            "result": result,
                        },
                    )
                )

                if isinstance(result, str):
                    content = result
                else:
                    content = json.dumps(
                        result,
                        ensure_ascii=False,
                        default=str,
                    )

            except Exception as error:
                print(
                    "\n[TOOL EXECUTION ERROR]"
                )
                print(
                    "NAME:",
                    name,
                )
                print(
                    "ARGUMENTS:",
                    arguments,
                )
                print(
                    type(error).__name__,
                    ":",
                    str(error),
                )

                content = json.dumps(
                    {
                        "error": str(error),
                    },
                    ensure_ascii=False,
                )

                self.emit(
                    Event(
                        type=EventType.ERROR,
                        data=str(error),
                    )
                )

            results.append(
                {
                    "role": "tool",
                    "tool_name": name,
                    "content": content,
                }
            )

        return results

    def _extract_memories(
        self,
        user_message: str,
        assistant_response: str,
    ):
        prompt = f"""
You are PEVA's memory extraction system.

Analyze the conversation and identify ONLY information that
is useful for remembering about the user for future conversations.

Store things such as:
- name
- preferred name
- preferences
- hobbies
- important personal facts
- projects
- routines
- communication preferences
- language preferences
- response length preferences
- response style preferences
- personality preferences
- persistent instructions
- custom behaviors
- trigger-response instructions
- important goals

Communication preferences should be stored as category "preference".

Examples:
- "Talk to me casually."
- "Keep your answers short."
- "Use Hinglish when talking to me."
- "Explain coding concepts in detail."
- "Don't use emojis."
- "Be friendly but professional."

Return ONLY valid JSON.

If there is nothing worth remembering, return:
{{"memories": []}}

Otherwise return:
{{
    "memories": [
        {{
            "content": "short factual statement",
            "category": "identity|preference|personal_information|project|routine|instruction|goal|important_fact"
        }}
    ]
}}

User:
{user_message}

Assistant:
{assistant_response}
"""

        try:
            result = self.llm.generate_response(
                user_message=prompt,
                conversation=[],
            )

            result = result.strip()

            json_match = re.search(
                r"\{.*\}",
                result,
                re.DOTALL,
            )

            if not json_match:
                return

            data = json.loads(
                json_match.group(0)
            )

            memories = data.get(
                "memories",
                [],
            )

            if not isinstance(memories, list):
                return

            for item in memories:
                if not isinstance(item, dict):
                    continue

                content = item.get(
                    "content",
                    "",
                )

                category = item.get(
                    "category",
                    "general",
                )

                if not isinstance(content, str):
                    continue

                if not content.strip():
                    continue

                if not isinstance(category, str):
                    category = "general"

                self.memory.remember_semantic(
                    content=content.strip(),
                    category=category.strip()
                    or "general",
                )

        except Exception:
            return

    def _get_user_context(self) -> str:
        memories = (
            self.memory.get_all_semantic_memories()
        )

        identity = []
        preferences = []
        routines = []
        instructions = []
        goals = []

        for memory in memories:
            content = memory.content.strip()

            if not content:
                continue

            if memory.category == "identity":
                identity.append(
                    f"- {content}"
                )

            elif memory.category == "preference":
                preferences.append(
                    f"- {content}"
                )

            elif memory.category == "routine":
                routines.append(
                    f"- {content}"
                )

            elif memory.category == "instruction":
                instructions.append(
                    f"- {content}"
                )

            elif memory.category == "goal":
                goals.append(
                    f"- {content}"
                )

        sections = []

        if identity:
            sections.append(
                "Identity:\n"
                + "\n".join(identity)
            )

        if preferences:
            sections.append(
                "Communication and user preferences:\n"
                + "\n".join(preferences)
            )

        if routines:
            sections.append(
                "User routines:\n"
                + "\n".join(routines)
            )

        if instructions:
            sections.append(
                "Persistent user instructions:\n"
                + "\n".join(instructions)
            )

        if goals:
            sections.append(
                "User goals:\n"
                + "\n".join(goals)
            )

        return "\n\n".join(sections)

    def get_personalized_greeting(self) -> str:
        memories = (
            self.memory.get_all_semantic_memories()
        )

        user_context = []

        for memory in memories:
            if memory.category in {
                "identity",
                "preference",
                "routine",
                "instruction",
            }:
                user_context.append(
                    f"- {memory.content}"
                )

        context = "\n".join(
            user_context
        )

        prompt = f"""
You are PEVA, a personal AI assistant.

Generate a short, natural greeting for the user when PEVA wakes up.

Use the user's stored information when appropriate.

Rules:
- Keep it natural and concise.
- Address the user by their preferred name if known.
- Follow any stored greeting preference.
- Do not mention memories or instructions.
- Do not explain anything.
- Return only the greeting.
- Do not use quotation marks.

User information:
{context}
"""

        try:
            response = self.llm.generate_response(
                user_message=prompt,
                conversation=[],
            )

            response = response.strip()

            if response:
                return response

        except Exception:
            pass

        return "Hello! I'm PEVA."

    def get_personalized_goodbye(self) -> str:
        memories = (
            self.memory.get_all_semantic_memories()
        )

        instruction = ""

        for memory in memories:
            if memory.category != "instruction":
                continue

            content = memory.content.strip()

            if (
                "goodbye" in content.lower()
                or "good night" in content.lower()
                or "bye" in content.lower()
            ):
                instruction = content
                break

        if not instruction:
            return (
                "Goodbye! I'll be here when you need me."
            )

        prompt = f"""
You are PEVA, a personal AI assistant.

Generate a short, natural goodbye based on the user's
stored instruction below.

Do not mention that you are following an instruction.
Do not explain anything.
Return only the sentence PEVA should say.

Stored instruction:
{instruction}
"""

        try:
            response = self.llm.generate_response(
                user_message=prompt,
                conversation=[],
            )

            response = response.strip()

            if response:
                return response

        except Exception:
            pass

        return (
            "Goodbye! I'll be here when you need me."
        )
    def voice_chat(self) -> dict:
        self.start_listening()

        audio_path = (
            "data/logs/peva_voice_input.wav"
        )

        recording = self.microphone.record_until_silence(
            output_path=audio_path,
            max_duration=15.0,
            silence_duration=1.2,
            start_timeout=5.0,
        )

        if not recording.get("success"):
            self.runtime.set_state(
                PEVAState.AWAKE
            )

            return {
                "success": False,
                "stage": "recording",
                "message": recording.get(
                    "message",
                    "Microphone recording failed.",
                ),
            }

        self.start_processing()

        transcription = self.stt.transcribe(
            audio_path
        )

        if not transcription.get("success"):
            self.runtime.set_state(
                PEVAState.AWAKE
            )

            return {
                "success": False,
                "stage": "transcription",
                "message": transcription.get(
                    "message",
                    "Speech transcription failed.",
                ),
            }

        text = transcription.get(
            "text",
            "",
        ).strip()

        if not text:
            self.runtime.set_state(
                PEVAState.AWAKE
            )

            return {
                "success": False,
                "stage": "transcription",
                "message": "No speech detected.",
            }

        response = self.chat(
            text
        )

        return {
            "success": True,
            "text": text,
            "language": transcription.get(
                "language"
            ),
            "confidence": transcription.get(
                "confidence",
                0.0,
            ),
            "response": response,
        }
    def chat(
        self,
        user_message: str,
    ) -> str:
        if (
            not user_message
            or not user_message.strip()
        ):
            raise ValueError(
                "User message cannot be empty"
            )

        user_message = user_message.strip()

        self.start_processing()

        try:
            relevant_memories = self.memory.search(
                query=user_message,
                top_k=5,
                min_score=0.3,
            )

            memory_context = ""

            if relevant_memories:
                memory_context = "\n".join(
                    f"- {result.memory.content}"
                    for result in relevant_memories
                )

            self.conversation.add_user_message(
                user_message
            )

            user_context = (
                self._get_user_context()
            )

            tool_definitions = (
                self._build_tool_definitions()
            )

            messages_history = (
                self.llm.build_tool_messages(
                    user_message=user_message,
                    conversation=(
                        self.conversation
                        .get_messages()[:-1]
                    ),
                    memory=memory_context,
                    user_context=user_context,
                )
            )

            response = self.llm.chat_messages(
                messages=messages_history,
                tools=tool_definitions
                if tool_definitions
                else None,
            )

            max_tool_rounds = 5
            tool_round = 0

            while tool_round < max_tool_rounds:
                message = response.get(
                    "message",
                    {},
                )

                tool_calls = message.get(
                    "tool_calls",
                    [],
                )

                if not tool_calls:
                    break

                messages_history.append(
                    message
                )

                tool_results = (
                    self._execute_tool_calls(
                        tool_calls
                    )
                )

                messages_history.extend(
                    tool_results
                )

                response = (
                    self.llm.chat_messages(
                        messages=messages_history,
                        tools=tool_definitions
                        if tool_definitions
                        else None,
                    )
                )

                tool_round += 1

            final_message = response.get(
                "message",
                {},
            )

            response_text = final_message.get(
                "content",
                "",
            ).strip()

            if not response_text:
                response_text = (
                    "I completed the requested "
                    "tool operation."
                )

            self.conversation.add_assistant_message(
                response_text
            )

            self._extract_memories(
                user_message=user_message,
                assistant_response=response_text,
            )

            self.emit(
                Event(
                    type=EventType.RESPONSE_READY,
                    data=response_text,
                )
            )
            self.tts.speak(
                response_text
            )

            return response_text

        except Exception as error:
            print(
                "\n[PEVA TOOL ERROR]"
            )
            print(
                type(error).__name__,
                ":",
                str(error),
            )

            self.emit(
                Event(
                    type=EventType.ERROR,
                    data=str(error),
                )
            )

            raise

        finally:
            self.runtime.set_state(
                PEVAState.AWAKE
            )


    def remember(
        self,
        key: str,
        value,
    ):
        self.memory.remember(
            key,
            value,
        )

    def recall(
        self,
        key: str,
        default=None,
    ):
        return self.memory.recall(
            key,
            default,
        )

    def remember_semantic(
        self,
        content: str,
        category: str = "general",
    ):
        return self.memory.remember_semantic(
            content,
            category,
        )

    def search_memory(
        self,
        query: str,
        top_k: int = 5,
    ):
        return self.memory.search(
            query=query,
            top_k=top_k,
        )

    def get_conversation(
        self,
    ) -> list[dict[str, str]]:
        return self.conversation.get_messages()

    def get_state(self) -> PEVAState:
        return self.runtime.state

    def is_chat_open(self) -> bool:
        return self.runtime.chat_open