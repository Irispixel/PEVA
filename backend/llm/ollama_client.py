import requests

from backend.core.config import OLLAMA_HOST, LLM_MODEL
from backend.llm.prompts import build_messages


class OllamaClient:
    def __init__(
        self,
        host: str = OLLAMA_HOST,
        model: str = LLM_MODEL,
    ):
        self.host = host.rstrip("/")
        self.model = model
        self.chat_url = f"{self.host}/api/chat"

    def chat(
        self,
        messages: list[dict],
        stream: bool = False,
        tools: list[dict] | None = None,
    ) -> dict:
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": stream,
        }

        if tools:
            payload["tools"] = tools

        response = requests.post(
            self.chat_url,
            json=payload,
            timeout=300,
        )

        response.raise_for_status()

        return response.json()

    def generate_response(
        self,
        user_message: str,
        conversation: list[dict] | None = None,
        memory: str = "",
        user_context: str = "",
        desktop_context: str = "",
        tools: list[dict] | None = None,
    ) -> str:
        messages = build_messages(
            user_message=user_message,
            conversation=conversation,
            memory=memory,
            user_context=user_context,
            desktop_context=desktop_context,
        )

        response = self.chat(
            messages=messages,
            stream=False,
            tools=tools,
        )

        message = response.get(
            "message",
            {},
        )

        content = message.get(
            "content",
            "",
        )

        return content.strip()

    def generate_with_tools(
        self,
        user_message: str,
        conversation: list[dict] | None = None,
        memory: str = "",
        user_context: str = "",
        desktop_context: str = "",
        tools: list[dict] | None = None,
    ) -> dict:
        messages = build_messages(
            user_message=user_message,
            conversation=conversation,
            memory=memory,
            user_context=user_context,
            desktop_context=desktop_context,
        )

        return self.chat(
            messages=messages,
            stream=False,
            tools=tools,
        )
    def chat_messages(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        return self.chat(
            messages=messages,
            stream=False,
            tools=tools,
        )
    def build_tool_messages(
        self,
        user_message: str,
        conversation: list[dict] | None = None,
        memory: str = "",
        user_context: str = "",
        desktop_context: str = "",
    ) -> list[dict]:
        return build_messages(
            user_message=user_message,
            conversation=conversation,
            memory=memory,
            user_context=user_context,
            desktop_context=desktop_context,
        )


    def is_available(self) -> bool:
        try:
            response = requests.get(
                self.host,
                timeout=5,
            )

            return response.ok

        except requests.RequestException:
            return False