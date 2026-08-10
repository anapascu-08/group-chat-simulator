"""Orchestrare multi-persona: fiecare persona răspunde pe rând, cu context complet."""

from conversation import Conversation
from ollama_client import generate_response as _default_generate_response


def respond_as(
    conversation: Conversation,
    persona: dict,
    generate_response=_default_generate_response,
) -> str:
    """O persona generează un răspuns, îl adaugă în conversație și îl întoarce.

    Fiindcă adaugă răspunsul direct în `conversation`, o persona apelată
    ulterior în aceeași rundă vede automat răspunsurile date deja de
    celelalte personas (via `conversation.messages_for`).
    """
    reply = generate_response(
        system_prompt=persona["system_prompt"],
        messages=conversation.messages_for(persona["name"]),
        temperature=persona["temperature"],
    )
    conversation.add_message(persona["name"], reply)
    return reply
