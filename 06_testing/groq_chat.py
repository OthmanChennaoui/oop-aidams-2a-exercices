"""Appel à l'API Groq — le client est injectable pour pouvoir le mocker.

`groq` n'est importé que si aucun client n'est fourni : les tests (qui
passent un faux client) n'ont donc besoin ni du paquet, ni d'une clé API,
ni d'internet.
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
        from groq import Groq  # import paresseux : pip install groq

        client = Groq()  # lit GROQ_API_KEY dans l'environnement

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": question}],
        max_tokens=MAX_TOKENS,
    )
    return response.choices[0].message.content
