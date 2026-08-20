"""Euristică de relevanță: care personas ar reacționa plauzibil la un mesaj."""

import re

_WORD_RE = re.compile(r"\w+", re.UNICODE)

_STOPWORDS = {
    "și", "sau", "un", "o", "un", "cu", "la", "de", "din", "pe", "în", "ce",
    "cine", "care", "despre", "pentru", "e", "este", "sunt", "ai", "are",
    "să", "se", "nu", "da", "mai", "ca", "dar", "am", "ați", "eu", "tu",
    "el", "ea", "noi", "voi", "ei", "ele", "al", "a", "the", "și-",
    # cuvinte generice care apar în personality/bio ca umplutură de stil
    # ("are o părere despre orice"), nu ca semnal tematic real — dacă rămân
    # aici, orice mesaj banal care le folosește ("ce părere aveți?") s-ar
    # potrivi accidental cu o singură persona și ar bloca fallback-ul la toți
    "părere", "orice",
}


def _tokenize(text: str) -> set[str]:
    return {w.lower() for w in _WORD_RE.findall(text)} - _STOPWORDS


def _persona_keywords(persona: dict) -> set[str]:
    return _tokenize(f"{persona['personality']} {persona['bio']}")


def relevant_personas(text: str, personas: list[dict]) -> list[dict]:
    """Personas a căror personality/bio se suprapune cu mesajul.

    Dacă niciuna nu se potrivește, se întorc toate — un mesaj banal ("Ce
    faceți diseară?") nu ar trebui să lase chat-ul mut.
    """
    message_words = _tokenize(text)
    matched = [p for p in personas if _persona_keywords(p) & message_words]
    return matched if matched else list(personas)
