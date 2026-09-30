"""Groq API client for answer generation."""

import os
import streamlit as st
from dotenv import load_dotenv
from groq import Groq

load_dotenv()


class LLMClient:
    """Client for the Groq LLM API."""

    def __init__(self):
        """Initialize the Groq client with API key."""

        # Local .env first
        self.api_key = os.getenv("GROQ_API_KEY")

        # Streamlit Cloud Secrets fallback
        if not self.api_key:
            try:
                self.api_key = st.secrets["GROQ_API_KEY"]
            except (KeyError, FileNotFoundError):
                self.api_key = None

        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. "
                "Add it to Streamlit Secrets or your local .env file."
            )

        self.client = Groq(api_key=self.api_key)

    def generate(self, system_prompt: str, user_message: str) -> str:
        """Generate an answer using the Groq LLM."""

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