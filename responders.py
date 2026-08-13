"""Decide cine răspunde la un mesaj: mențiuni explicite @nume, cu prioritate
absolută, altfel euristica de relevanță tematică."""

from mentions import has_mention, mentioned_personas
from routing import relevant_personas


def select_responders(text: str, personas: list[dict]) -> list[dict]:
    if has_mention(text):
        return mentioned_personas(text, personas)
    return relevant_personas(text, personas)
