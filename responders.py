"""Decide cine răspunde la un mesaj: mențiuni explicite @nume, cu prioritate
absolută, altfel euristica de relevanță tematică."""

import random

from mentions import has_mention, mentioned_personas
from routing import relevant_personas

MENTIONED_SHARE = 0.8
UNMENTIONED_SHARE = 0.2


def response_probabilities(text: str, personas: list[dict]) -> dict[str, float]:
    """Probabilitatea, per persona, de a răspunde la un mesaj cu mențiuni @nume.

    Grupul menționat își împarte în total MENTIONED_SHARE, grupul nemenționat
    își împarte restul — egal între membrii fiecărui grup. Dacă un grup e gol,
    celălalt primește 100%. Dacă mențiunea nu se potrivește nicio persona,
    nimeni nu primește șansă de răspuns.
    """
    mentioned = mentioned_personas(text, personas)
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


def select_responders(text: str, personas: list[dict], rng=random.random) -> list[dict]:
    """Cine răspunde la un mesaj.

    Cu mențiuni @nume, fiecare persona decide independent, cu propria
    probabilitate din `response_probabilities` (Bernoulli — pot răspunde 0,
    una, mai multe sau toate). Fără mențiuni, cade pe euristica de relevanță
    din `routing.py` (deterministă).
    """
    if has_mention(text):
        probs = response_probabilities(text, personas)
        return [p for p in personas if rng() < probs[p["name"]]]
    return relevant_personas(text, personas)
