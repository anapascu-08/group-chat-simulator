from responders import response_probabilities, select_responders

PERSONAS = [
    {"name": "Nea Fănică", "personality": "haios, jovial, vorbește în metafore", "bio": "Cântăreț de muzică populară"},
    {
        "name": "Mircea Eliade",
        "personality": "erudit, filosofic, vorbește despre mit, sacru și istoria religiilor",
        "bio": "Istoric al religiilor, filozof și scriitor",
    },
    {"name": "Robi", "personality": "descurcăreț, vorbește în șpagă, mereu cu ochii pe un ban în plus", "bio": "Un smecheraș care vrea să facă și el un ban"},
]


def test_no_mention_falls_back_to_relevance():
    result = select_responders("Ce ziceți despre mit și religie?", PERSONAS)
    assert result == [PERSONAS[1]]


def test_no_mention_and_no_relevance_match_returns_all():
    result = select_responders("Ce faceți diseară?", PERSONAS)
    assert result == PERSONAS


def test_one_mentioned_of_three_splits_80_10_10():
    probs = response_probabilities("@Robi ce zici de religie?", PERSONAS)
    assert probs == {"Nea Fănică": 0.1, "Mircea Eliade": 0.1, "Robi": 0.8}


def test_two_mentioned_of_three_splits_40_40_20():
    probs = response_probabilities("@Robi @Fănică ce ziceți?", PERSONAS)
    assert probs == {"Nea Fănică": 0.4, "Robi": 0.4, "Mircea Eliade": 0.2}


def test_all_mentioned_splits_evenly_to_100_percent():
    probs = response_probabilities("@Robi @Fănică @Eliade salut", PERSONAS)
    assert probs == {"Nea Fănică": 1 / 3, "Mircea Eliade": 1 / 3, "Robi": 1 / 3}


def test_mention_matching_nobody_gives_everyone_zero_probability():
    probs = response_probabilities("@cineva salut", PERSONAS)
    assert probs == {"Nea Fănică": 0.0, "Mircea Eliade": 0.0, "Robi": 0.0}


def test_mention_matching_nobody_returns_none_regardless_of_rng():
    # rng=0.0 ar selecta pe oricine cu probabilitate > 0 — aici nimeni nu are
    result = select_responders("@cineva ce zici de religie?", PERSONAS, rng=lambda: 0.0)
    assert result == []


def test_select_responders_applies_probability_threshold_via_injected_rng():
    # @Robi -> 0.8, ceilalți -> 0.1 fiecare
    values = iter([0.05, 0.5, 0.79])  # Fănică(0.1): sub prag; Eliade(0.1): peste prag; Robi(0.8): sub prag
    result = select_responders("@Robi ce zici de religie?", PERSONAS, rng=lambda: next(values))
    assert result == [PERSONAS[0], PERSONAS[2]]


def test_select_responders_uses_default_rng_when_not_injected():
    result = select_responders("@Robi ce zici de religie?", PERSONAS)
    assert all(p in PERSONAS for p in result)
