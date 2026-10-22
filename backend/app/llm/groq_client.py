import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()


class GroqClient:
    """
    Low-level client responsible for communication
    with the Groq API.
    """

    def __init__(
        self,
        model: str = "openai/gpt-oss-20b",
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=api_key
        )

        self.model = model

    def generate(
        self,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> str:

        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
        )

        content = response.choices[0].message.content

        # Some models (e.g. reasoning models) can return no text
        # content. Always hand a string back to the callers.
        return content or ""