"""Decide cine răspunde la un mesaj: mențiuni explicite @nume, cu prioritate
absolută, altfel euristica de relevanță tematică."""

import random

from mentions import has_mention, mentioned_personas
from routing import relevant_personas

UNMENTIONED_SHARE = 0.2


def pending_mentions(history: list[dict], personas: list[dict]) -> list[dict]:
    """Personas menționate (de oricine — user sau altă persona) de la ultimul
    lor mesaj încoace, care încă n-au apucat să răspundă.

    Dacă o persona nu a vorbit niciodată, se ia în calcul tot istoricul. O
    mențiune rămâne "activă" oricât ar dura, până persona vorbește din nou —
    apoi se consideră consumată.
    """
    pending = []
    for persona in personas:
        last_spoken = -1
        for i, msg in enumerate(history):
            if msg["name"] == persona["name"]:
                last_spoken = i
        text_since = " ".join(m["content"] for m in history[last_spoken + 1 :])
        if has_mention(text_since) and persona in mentioned_personas(text_since, personas):
            pending.append(persona)
    return pending


def response_probabilities(history: list[dict], personas: list[dict]) -> dict[str, float]:
    """Probabilitatea, per persona, de a răspunde, pe baza mențiunilor active.

    Personas menționate (vezi `pending_mentions`) au probabilitate 1.0 —
    răspund garantat, indiferent câte mesaje au trecut de la mențiune. Cele
    nemenționate își împart UNMENTIONED_SHARE în mod egal, ca să mai poată
    interveni ocazional. Dacă nimeni nu are o mențiune activă, toți primesc
    0 (apelantul ar trebui să cadă pe euristica de relevanță, vezi
    `select_responders`).
    """
    mentioned = pending_mentions(history, personas)
    if not mentioned:
        return {p["name"]: 0.0 for p in personas}

    mentioned_names = {p["name"] for p in mentioned}
    unmentioned = [p for p in personas if p["name"] not in mentioned_names]

    probs = {name: 1.0 for name in mentioned_names}
    if unmentioned:
        share = UNMENTIONED_SHARE / len(unmentioned)
        probs.update({p["name"]: share for p in unmentioned})
    return probs


def select_responders(history: list[dict], personas: list[dict], rng=random.random) -> list[dict]:
    """Cine răspunde, pe baza istoricului complet al conversației.

    Dacă există mențiuni active (curente sau mai vechi, nerăspunse încă —
    vezi `pending_mentions`), toate personas menționate răspund garantat,
    indiferent câte mesaje au trecut de la mențiune. Cele nemenționate mai
    pot interveni ocazional, fiecare cu propria probabilitate din
    `response_probabilities` (Bernoulli, folosind partea UNMENTIONED_SHARE
    din probabilități). Dacă ultimul mesaj conține o mențiune care nu se
    potrivește nicio persona (și nimeni altcineva nu are o mențiune
    activă), nu răspunde nimeni. Altfel, cade pe euristica de relevanță din
    `routing.py` (deterministă), aplicată pe ultimul mesaj.
    """
    last_message = history[-1]["content"] if history else ""

    mentioned = pending_mentions(history, personas)
    if mentioned:
        mentioned_names = {p["name"] for p in mentioned}
        probs = response_probabilities(history, personas)
        extra = [p for p in personas if p["name"] not in mentioned_names and rng() < probs[p["name"]]]
        return mentioned + extra
    if has_mention(last_message):
        return []
    return relevant_personas(last_message, personas)
