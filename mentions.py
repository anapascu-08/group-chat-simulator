"""Detectează la ce personas s-a referit un mesaj prin mențiuni @nume."""

import re

_MENTION_RE = re.compile(r"@(\w+)", re.UNICODE)


def _name_tokens(name: str) -> set[str]:
    """Formele pe care le poate lua numele unei persona într-o mențiune.

    Ex. pentru "Nea Fănică": {"nea", "fănică", "neafănică"} — ca "@Fănică"
    sau "@NeaFănică" să funcționeze la fel de bine.
    """
    tokens = {word.lower() for word in name.split()}
    tokens.add(name.replace(" ", "").lower())
    return tokens


def mentioned_personas(text: str, personas: list[dict]) -> list[dict]:
    """Personas menționate explicit în text cu @nume.

    Dacă nu există nicio mențiune @, se întorc toate personas (comportamentul
    implicit). Dacă există mențiuni dar niciuna nu se potrivește vreunei
    persona, nu răspunde nimeni.
    """
    mentions = {m.lower() for m in _MENTION_RE.findall(text)}
    if not mentions:
        return list(personas)

    return [p for p in personas if _name_tokens(p["name"]) & mentions]
