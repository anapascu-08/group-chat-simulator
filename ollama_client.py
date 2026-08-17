"""Singurul modul care vorbește direct cu Ollama."""

import json
import os

import httpx

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "gemma4:e2b")


def generate_response(
    system_prompt: str,
    messages: list[dict],
    temperature: float = 0.9,
) -> str:
    """Generează un răspuns pentru o persona.

    `messages` e istoricul conversației din perspectiva personei curente,
    ca listă de mesaje {"role": "user" | "assistant", "content": str}.
    """
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [{"role": "system", "content": system_prompt}, *messages],
        "stream": False,
        "options": {"temperature": temperature},
        "think": False,
    }
    response = httpx.post(f"{OLLAMA_HOST}/api/chat", json=payload, timeout=120)
    response.raise_for_status()
    return response.json()["message"]["content"].strip()


if __name__ == "__main__":
    with open("personas.json", encoding="utf-8") as f:
        persona = json.load(f)[0]

    print(f"Testez persona: {persona['name']}")
    reply = generate_response(
        system_prompt=persona["system_prompt"],
        messages=[{"role": "user", "content": "Salut! Ce mai faci?"}],
        temperature=persona["temperature"],
    )
    print(f"{persona['name']}: {reply}")
