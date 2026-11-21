"""Call to the Groq API - the client is injectable so that it can be mocked.

`groq` is only imported when no client is given: the tests (which pass a
fake client) therefore need neither the package, nor an API key, nor
internet access.
"""

from __future__ import annotations

from typing import Any

MODEL = "llama-3.3-70b-versatile"
MAX_TOKENS = 1024


def ask_groq(question: str, client: Any = None) -> str:
    """Send a question to Groq and return the answer."""
    if not question.strip():
        raise ValueError("Question cannot be empty")

    if client is None:
        from groq import Groq  # lazy import: pip install groq

        client = Groq()  # reads GROQ_API_KEY from the environment

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content
