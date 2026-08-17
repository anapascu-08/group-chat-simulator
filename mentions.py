"""Detectează la ce personas s-a referit un mesaj prin mențiuni @nume."""

import re
import unicodedata

_MENTION_RE = re.compile(r"@(\w+)", re.UNICODE)


def _fold(text: str) -> str:
    """Lowercase și fără diacritice, ca "@Fănică" și "@Fanica" să se potrivească la fel."""
    decomposed = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in decomposed if not unicodedata.combining(c))


def _name_tokens(name: str) -> set[str]:
    """Formele pe care le poate lua numele unei persona într-o mențiune.

    Ex. pentru "Nea Fănică": {"nea", "fanica", "neafanica"} — ca "@Fănică",
    "@Fanica" sau "@NeaFănică" să funcționeze la fel de bine.
    """
    tokens = {_fold(word) for word in name.split()}
    tokens.add(_fold(name.replace(" ", "")))
    return tokens


def has_mention(text: str) -> bool:
    """Dacă mesajul conține cel puțin o mențiune @nume."""
    return bool(_MENTION_RE.search(text))


def mentioned_personas(text: str, personas: list[dict]) -> list[dict]:
    """Personas menționate explicit în text cu @nume.

    Mențiunea poate fi doar un prefix al numelui (ex. "@can" pentru
    "Cântărețul"), nu neapărat numele întreg.

    Dacă nu există nicio mențiune @, se întorc toate personas (comportamentul
    implicit). Dacă există mențiuni dar niciuna nu se potrivește vreunei
    persona, nu răspunde nimeni.
    """
    mentions = {_fold(m) for m in _MENTION_RE.findall(text)}
    if not mentions:
        return list(personas)

    return [
        p
        for p in personas
        if any(token.startswith(m) for token in _name_tokens(p["name"]) for m in mentions)
    ]
