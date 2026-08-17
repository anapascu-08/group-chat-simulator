"""Decide cine răspunde la un mesaj: mențiuni explicite @nume, cu prioritate
absolută, altfel euristica de relevanță tematică."""

import random

from mentions import has_mention, mentioned_personas
from routing import relevant_personas

MENTIONED_SHARE = 0.8
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

    Grupul menționat (vezi `pending_mentions`) își împarte în total
    MENTIONED_SHARE, grupul nemenționat își împarte restul — egal între
    membrii fiecărui grup. Dacă un grup e gol, celălalt primește 100%. Dacă
    nimeni nu are o mențiune activă, toți primesc 0 (apelantul ar trebui să
    cadă pe euristica de relevanță, vezi `select_responders`).
    """
    mentioned = pending_mentions(history, personas)
    if not mentioned:
        return {p["name"]: 0.0 for p in personas}

    mentioned_names = {p["name"] for p in mentioned}
    unmentioned = [p for p in personas if p["name"] not in mentioned_names]

    if unmentioned:
        mentioned_total, unmentioned_total = MENTIONED_SHARE, UNMENTIONED_SHARE
    else:
        mentioned_total, unmentioned_total = 1.0, 0.0

    probs = {p["name"]: mentioned_total / len(mentioned) for p in mentioned}
    if unmentioned:
        share = unmentioned_total / len(unmentioned)
        probs.update({p["name"]: share for p in unmentioned})
    return probs


def select_responders(history: list[dict], personas: list[dict], rng=random.random) -> list[dict]:
    """Cine răspunde, pe baza istoricului complet al conversației.

    Dacă există mențiuni active (curente sau mai vechi, nerăspunse încă —
    vezi `pending_mentions`), fiecare persona decide independent, cu propria
    probabilitate din `response_probabilities` (Bernoulli — pot răspunde 0,
    una, mai multe sau toate). Dacă ultimul mesaj conține o mențiune care nu
    se potrivește nicio persona (și nimeni altcineva nu are o mențiune
    activă), nu răspunde nimeni. Altfel, cade pe euristica de relevanță din
    `routing.py` (deterministă), aplicată pe ultimul mesaj.
    """
    last_message = history[-1]["content"] if history else ""

    mentioned = pending_mentions(history, personas)
    if mentioned:
        probs = response_probabilities(history, personas)
        return [p for p in personas if rng() < probs[p["name"]]]
    if has_mention(last_message):
        return []
    return relevant_personas(last_message, personas)
