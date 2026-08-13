"""Orchestrare multi-persona: fiecare persona răspunde pe rând, cu context complet."""

import re
from typing import Optional

from conversation import Conversation
from ollama_client import generate_response as _default_generate_response

BEHAVIOR_GUIDELINES = (
    "Rămâi tot timpul în rolul descris mai sus. Răspunde scurt — 1 paragraf, "
    "maxim 2 —, direct la subiectul ultimului mesaj din conversație. Nu te "
    "prezenta din nou dacă ai mai vorbit deja în conversație. Scrie ca într-un "
    "mesaj normal de chat, text simplu — fără markdown (fără **, #, liste cu -)."
)

FALLBACK_REPLY = "..."
MAX_ATTEMPTS = 3

_BOLD_RE = re.compile(r"\*\*(.+?)\*\*|__(.+?)__")
_INLINE_CODE_RE = re.compile(r"`([^`]+)`")
_HEADER_RE = re.compile(r"^#{1,6}\s*", flags=re.MULTILINE)
_BULLET_RE = re.compile(r"^[*\-]\s+", flags=re.MULTILINE)


def humanize(text: str) -> str:
    """Curăță formatarea markdown pe care modelele o mai strecoară în răspuns,
    ca mesajul să sune ca într-un chat normal, nu ca o notiță scrisă."""
    text = _BOLD_RE.sub(lambda m: m.group(1) or m.group(2), text)
    text = _INLINE_CODE_RE.sub(r"\1", text)
    text = _HEADER_RE.sub("", text)
    text = _BULLET_RE.sub("", text)
    return text.strip()


def _generate_and_humanize(generate_response, system_prompt, messages, temperature) -> str:
    raw = generate_response(system_prompt=system_prompt, messages=messages, temperature=temperature)
    return humanize(raw)


def respond_as(
    conversation: Conversation,
    persona: dict,
    target_message: Optional[dict] = None,
    generate_response=_default_generate_response,
) -> str:
    """O persona generează un răspuns, îl adaugă în conversație și îl întoarce.

    Fiindcă adaugă răspunsul direct în `conversation`, o persona apelată
    ulterior în aceeași rundă vede automat răspunsurile date deja de
    celelalte personas (via `conversation.messages_for`). Fără un
    `target_message` explicit, o persona apelată a doua/a treia oară în
    aceeași rundă ar interpreta ultimul mesaj din istoric — răspunsul unei
    alte persona — drept întrebarea la care trebuie să răspundă, și ar
    devia de la mesajul inițial al utilizatorului. Punem mesajul-țintă ca
    etichetă scurtă în system prompt (nu ca mesaj nou în listă) — modelele
    mici testate devin mult mai predispuse la răspunsuri goale pe măsură ce
    crește numărul de mesaje consecutive de tip "user" în listă.
    """
    system_prompt = f"{persona['system_prompt']}\n\n{BEHAVIOR_GUIDELINES}"
    if target_message:
        system_prompt += f"\n\nSubiectul discuției: {target_message['content']}"
    messages = conversation.messages_for(persona["name"])

    reply = ""
    for _ in range(MAX_ATTEMPTS):
        # modelele mici generează ocazional un răspuns gol; reîncercăm de câteva
        # ori, fiindcă generarea e non-deterministă (temperature > 0)
        reply = _generate_and_humanize(generate_response, system_prompt, messages, persona["temperature"])
        if reply:
            break
    if not reply:
        reply = FALLBACK_REPLY

    conversation.add_message(persona["name"], reply)
    return reply
