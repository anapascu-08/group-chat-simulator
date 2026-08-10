"""Orchestrare multi-persona: fiecare persona răspunde pe rând, cu context complet."""

from conversation import Conversation
from ollama_client import generate_response as _default_generate_response

BEHAVIOR_GUIDELINES = (
    "Rămâi tot timpul în rolul descris mai sus. Răspunde scurt (1-3 propoziții), "
    "direct la subiectul ultimului mesaj din conversație. Nu te prezenta din nou "
    "dacă ai mai vorbit deja în conversație."
)

FALLBACK_REPLY = "..."


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
    system_prompt = f"{persona['system_prompt']}\n\n{BEHAVIOR_GUIDELINES}"
    messages = conversation.messages_for(persona["name"])

    reply = generate_response(
        system_prompt=system_prompt, messages=messages, temperature=persona["temperature"]
    )
    if not reply.strip():
        # modelele mici generează ocazional un răspuns gol; o reîncercare rezolvă
        # de obicei, fiindcă generarea e non-deterministă (temperature > 0)
        reply = generate_response(
            system_prompt=system_prompt, messages=messages, temperature=persona["temperature"]
        )
    if not reply.strip():
        reply = FALLBACK_REPLY

    conversation.add_message(persona["name"], reply)
    return reply
