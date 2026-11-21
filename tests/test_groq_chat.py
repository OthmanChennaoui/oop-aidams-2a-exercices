"""Mocking: replace the real Groq client with a fake one that is fast and free."""

import os

import pytest

from groq_chat import MAX_TOKENS, MODEL, ask_groq


def test_ask_groq(fake_groq_client):
    answer = ask_groq("What is 2+2?", client=fake_groq_client)
    assert answer == "4"


def test_ask_groq_calls_api_correctly(fake_groq_client):
    ask_groq("What is 2+2?", client=fake_groq_client)

    fake_groq_client.chat.completions.create.assert_called_once_with(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": "What is 2+2?"}],
        max_tokens=1024,
    )
    assert (MODEL, MAX_TOKENS) == ("llama-3.3-70b-versatile", 1024)


def test_ask_groq_raises_error_when_api_fails(mocker):
    mock_client = mocker.Mock()
    mock_client.chat.completions.create.side_effect = Exception("API down")

    with pytest.raises(Exception, match="API down"):
        ask_groq("What is 2+2?", client=mock_client)


@pytest.mark.parametrize("question", ["", "   ", "\n"])
def test_ask_groq_rejects_empty_question(question, fake_groq_client):
    with pytest.raises(ValueError, match="cannot be empty"):
        ask_groq(question, client=fake_groq_client)
    fake_groq_client.chat.completions.create.assert_not_called()


@pytest.mark.slow
@pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
def test_ask_groq_real_api():
    """Real network call: only run with `pytest -m slow`."""
    pytest.importorskip("groq")
    assert "4" in ask_groq("What is 2+2? Answer with a single digit.")
