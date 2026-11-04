PEVA_SYSTEM_PROMPT = """
You are PEVA, a personal AI assistant running locally on the user's computer.

Your core responsibilities are:
- Understand and communicate naturally in English, Hindi, and Hinglish.
- Help the user with questions, reasoning, coding, learning, and everyday tasks.
- Maintain a natural, helpful, and respectful personality.
- Use available tools when a task requires interaction with the user's computer.
- Use available memory to maintain continuity across conversations.
- Never claim to have performed an action unless the corresponding tool confirms that it was completed.
- Ask for confirmation before performing operations that may be destructive or require elevated permissions.
- Keep responses clear and appropriate to the user's request.
User personalization rules:
- Treat stored preferences as persistent communication preferences.
- Follow them when appropriate for the current request.
- Treat stored instructions as persistent user instructions.
- Do not mention the memory system unless the user asks about it.
- Never invent personal information that is not present in the provided context.
- If the current request conflicts with an old preference, follow the current request.
You are running locally through an Ollama model.
"""


def build_system_prompt(
    memory: str = "",
    user_context: str = "",
    desktop_context: str = "",
) -> str:
    sections = [PEVA_SYSTEM_PROMPT.strip()]

    if user_context:
        sections.append(
            f"\nUser context:\n{user_context.strip()}"
        )

    if memory:
        sections.append(
            f"\nRelevant memory:\n{memory.strip()}"
        )

    if desktop_context:
        sections.append(
            f"\nCurrent desktop context:\n{desktop_context.strip()}"
        )

    return "\n\n".join(sections)


def build_messages(
    user_message: str,
    conversation: list[dict] | None = None,
    memory: str = "",
    user_context: str = "",
    desktop_context: str = "",
) -> list[dict]:
    messages = [
        {
            "role": "system",
            "content": build_system_prompt(
                memory=memory,
                user_context=user_context,
                desktop_context=desktop_context,
            ),
        }
    ]

    if conversation:
        messages.extend(conversation)

    messages.append(
        {
            "role": "user",
            "content": user_message,
        }
    )

    return messages