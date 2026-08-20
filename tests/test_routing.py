from personas_store import load_personas
from routing import relevant_personas

PERSONAS = [
    {"name": "Nea Fănică", "personality": "haios, jovial, vorbește în metafore", "bio": "Cântăreț de muzică populară"},
    {
        "name": "Mircea Eliade",
        "personality": "erudit, filosofic, vorbește despre mit, sacru și istoria religiilor",
        "bio": "Istoric al religiilor, filozof și scriitor",
    },
    {"name": "Robi", "personality": "descurcăreț, vorbește în șpagă, mereu cu ochii pe un ban în plus", "bio": "Un smecheraș care vrea să facă și el un ban"},
]


def test_persona_matching_bio_keyword_is_selected():
    result = relevant_personas("Ce ziceți despre mit și religie?", PERSONAS)
    assert result == [PERSONAS[1]]


def test_no_persona_matches_falls_back_to_all():
    result = relevant_personas("Ce faceți diseară?", PERSONAS)
    assert result == PERSONAS


def test_common_words_dont_cause_false_matches():
    # "și", "un", "la" apar în bio-uri, dar sunt stopwords — nu ar trebui
    # să declanșeze o potrivire pe un mesaj banal fără legătură tematică.
    result = relevant_personas("Și eu vreau la un film diseară", PERSONAS)
    assert result == PERSONAS


def test_multiple_matches_preserve_persona_order():
    result = relevant_personas("Cine cântă la muzică populară și cine face un ban?", PERSONAS)
    assert result == [PERSONAS[0], PERSONAS[2]]


def test_matching_ignores_case_and_punctuation():
    result = relevant_personas("RELIGIILE, mitul, istoria!", PERSONAS)
    assert result == [PERSONAS[1]]


def test_generic_bio_filler_words_dont_hijack_unrelated_questions():
    # "Taximetristul Gigi" are "are o părere despre orice" în bio — un mesaj
    # banal care folosește "părere" nu ar trebui să se potrivească doar cu el,
    # excluzând restul personas (regresie: doar Gigi răspundea la "Ce părere
    # aveți despre ultimele știri?", vezi personas.json).
    personas = load_personas()
    result = relevant_personas("Ați văzut ultimele știri? Ce părere aveți?", personas)
    assert result == personas
