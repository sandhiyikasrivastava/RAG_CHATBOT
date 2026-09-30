"""Conversation memory: keep last N messages and rewrite follow-up questions."""

from typing import List, Dict, Any
from config import MEMORY_LIMIT


class ConversationMemory:
    """Stores the last N messages and rewrites follow-up questions."""

    def __init__(self, limit: int = MEMORY_LIMIT):
        """Initialize conversation memory.

        Args:
            limit: Maximum number of messages to keep.
        """
        self.limit = limit
        self.messages: List[Dict[str, str]] = []

    def add(self, role: str, content: str):
        """Add a message to memory.

        Args:
            role: 'user' or 'assistant'.
            content: The message content.
        """
        self.messages.append({"role": role, "content": content})
        # Keep only the last N messages
        if len(self.messages) > self.limit:
            self.messages = self.messages[-self.limit:]

    def get_history(self) -> str:
        """Get the conversation history as a formatted string.

        Returns:
            Formatted conversation history.
        """
        if not self.messages:
            return ""

        lines = []
        for msg in self.messages:
            role = "User" if msg["role"] == "user" else "Bot"
            lines.append(f"{role}: {msg['content']}")
        return "\n".join(lines)

    def get_last_bot_message(self) -> str:
        """Get the last bot message.

        Returns:
            The last bot message content, or empty string if none.
        """
        for msg in reversed(self.messages):
            if msg["role"] == "assistant":
                return msg["content"]
        return ""

    def clear(self):
        """Clear all messages."""
        self.messages = []

    def is_empty(self) -> bool:
        """Check if memory is empty.

        Returns:
            True if no messages stored.
        """
        return len(self.messages) == 0

    def __len__(self) -> int:
        """Get the number of stored messages.

        Returns:
            Number of messages in memory.
        """
        return len(self.messages)


def rewrite_question(question: str, memory: ConversationMemory) -> str:
    """Rewrite a follow-up question using conversation history.

    Args:
        question: The user's question.
        memory: The conversation memory instance.

    Returns:
        The rewritten question (or original if no history).
    """
    if memory.is_empty():
        return question

    history = memory.get_history()
    last_bot_msg = memory.get_last_bot_message()

    # Simple pronoun resolution
    pronouns = ["it", "its", "they", "them", "their", "this", "that", "these", "those"]
    question_lower = question.lower()
    words = question_lower.split()

    # If question starts with a pronoun or is very short, try to rewrite
    if words and words[0] in pronouns or len(words) <= 5:
        if last_bot_msg:
            # Combine context with question
            return f"{question} (Context from previous answer: {last_bot_msg[:200]})"

    return question
