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


def _persona_tokens(persona: dict) -> set[str]:
    """Toate formele care pot identifica o persona într-o mențiune: numele din
    `personas.json` plus orice `aliases` (ex. porecla cu care se prezintă
    persona în propriul `system_prompt`, dacă diferă de `name`)."""
    tokens = _name_tokens(persona["name"])
    for alias in persona.get("aliases", []):
        tokens |= _name_tokens(alias)
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
        if any(token.startswith(m) for token in _persona_tokens(p) for m in mentions)
    ]


def strip_self_mentions(text: str, persona: dict) -> str:
    """Scoate @-ul din mențiunile în care o persona s-a taguiat pe ea însăși.

    Modelele mai strecoară, din obiceiul de a taguia pe oricine adresează, un
    @NumePropriu chiar când personajul vorbește despre sine — inclusiv sub
    porecla din propriul `system_prompt` (ex. Cântărețul Nae se prezintă
    "Nea Nae"), de-aia verificăm și `aliases`, nu doar `name`. Nu are sens ca
    cineva să apară taguit pe sine în chat, așa că păstrăm cuvântul dar
    scoatem @, ca să nu se mai randeze ca mențiune în UI.
    """
    own_tokens = _persona_tokens(persona)

    def _replace(match: re.Match) -> str:
        mention = match.group(1)
        if any(token.startswith(_fold(mention)) for token in own_tokens):
            return mention
        return match.group(0)

    return _MENTION_RE.sub(_replace, text)
