"""Groq API client for answer generation."""

import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMClient:
    """Client for the Groq LLM API."""

    def __init__(self):
        """Initialize the Groq client with API key from environment."""
        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. "
                "Please create a .env file with your Groq API key."
            )

        self.client = Groq(api_key=self.api_key)

    def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate an answer using the Groq LLM.

        Args:
            system_prompt: The system prompt with instructions and context.
            user_message: The user's question.

        Returns:
            The LLM's answer as a string.
        """
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=0.1,
            max_tokens=512,
        )
        return response.choices[0].message.content
