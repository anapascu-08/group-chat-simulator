from responders import pending_mentions, response_probabilities, select_responders

PERSONAS = [
    {"name": "Nea Fănică", "personality": "haios, jovial, vorbește în metafore", "bio": "Cântăreț de muzică populară"},
    {
        "name": "Mircea Eliade",
        "personality": "erudit, filosofic, vorbește despre mit, sacru și istoria religiilor",
        "bio": "Istoric al religiilor, filozof și scriitor",
    },
    {"name": "Robi", "personality": "descurcăreț, vorbește în șpagă, mereu cu ochii pe un ban în plus", "bio": "Un smecheraș care vrea să facă și el un ban"},
]


def hist(*pairs):
    return [{"name": name, "content": content} for name, content in pairs]


def test_no_mention_falls_back_to_relevance():
    history = hist(("Tu", "Ce ziceți despre mit și religie?"))
    result = select_responders(history, PERSONAS)
    assert result == [PERSONAS[1]]


def test_no_mention_and_no_relevance_match_returns_all():
    history = hist(("Tu", "Ce faceți diseară?"))
    result = select_responders(history, PERSONAS)
    assert result == PERSONAS


def test_one_mentioned_of_three_splits_50_10_10():
    history = hist(("Tu", "@Robi ce zici de religie?"))
    probs = response_probabilities(history, PERSONAS)
    assert probs == {"Nea Fănică": 0.1, "Mircea Eliade": 0.1, "Robi": 0.5}


def test_two_mentioned_of_three_splits_25_25_20():
    history = hist(("Tu", "@Robi @Fănică ce ziceți?"))
    probs = response_probabilities(history, PERSONAS)
    assert probs == {"Nea Fănică": 0.25, "Robi": 0.25, "Mircea Eliade": 0.2}


def test_all_mentioned_splits_evenly_to_100_percent():
    history = hist(("Tu", "@Robi @Fănică @Eliade salut"))
    probs = response_probabilities(history, PERSONAS)
    assert probs == {"Nea Fănică": 1 / 3, "Mircea Eliade": 1 / 3, "Robi": 1 / 3}


def test_mention_matching_nobody_returns_none_regardless_of_rng():
    history = hist(("Tu", "@cineva ce zici de religie?"))
    result = select_responders(history, PERSONAS, rng=lambda: 0.0)
    assert result == []


def test_select_responders_applies_probability_threshold_via_injected_rng():
    # @Robi -> 0.5, ceilalți -> 0.1 fiecare
    history = hist(("Tu", "@Robi ce zici de religie?"))
    values = iter([0.05, 0.5, 0.49])  # Fănică(0.1): sub prag; Eliade(0.1): peste prag; Robi(0.5): sub prag
    result = select_responders(history, PERSONAS, rng=lambda: next(values))
    assert result == [PERSONAS[0], PERSONAS[2]]


def test_guarantees_a_random_responder_when_all_bernoulli_draws_fail():
    # Toate tragerile pică (0.99 > orice prag) -> se alege totuși cineva, la
    # întâmplare din toate personas, folosind încă o tragere din rng.
    history = hist(("Tu", "@Robi ce zici de religie?"))
    values = iter([0.99, 0.99, 0.99, 0.5])  # ultima tragere -> index 1 din 3 -> Eliade
    result = select_responders(history, PERSONAS, rng=lambda: next(values))
    assert result == [PERSONAS[1]]


def test_all_mentioned_personas_can_all_respond_together():
    history = hist(("Tu", "@Robi @Fănică ce ziceți?"))
    result = select_responders(history, PERSONAS, rng=lambda: 0.0)
    assert result == PERSONAS


def test_select_responders_uses_default_rng_when_not_injected():
    history = hist(("Tu", "@Robi ce zici de religie?"))
    result = select_responders(history, PERSONAS)
    assert all(p in PERSONAS for p in result)


def test_mention_stays_pending_across_messages_until_persona_speaks():
    # @Eliade e menționat, dar userul mai trimite un mesaj fără @ înainte ca
    # Eliade să apuce să răspundă — mențiunea rămâne activă.
    history = hist(
        ("Tu", "@Eliade ce zici de mit?"),
        ("Robi", "las-o, frate, hai să vorbim de bani"),
        ("Tu", "serios acum"),
    )
    assert pending_mentions(history, PERSONAS) == [PERSONAS[1]]


def test_mention_is_consumed_once_persona_speaks():
    history = hist(
        ("Tu", "@Eliade ce zici de mit?"),
        ("Mircea Eliade", "Mitul e o structură arhetipală..."),
        ("Tu", "interesant"),
    )
    assert pending_mentions(history, PERSONAS) == []


def test_persona_can_mention_another_persona_and_it_stays_pending():
    history = hist(
        ("Tu", "ce ziceți?"),
        ("Nea Fănică", "hooo, @Robi ce zici tu de asta?"),
    )
    assert pending_mentions(history, PERSONAS) == [PERSONAS[2]]


def test_probabilities_use_pending_mention_from_earlier_message_without_current_at_symbol():
    history = hist(
        ("Tu", "@Robi ce faci?"),
        ("Tu", "alo, ești acolo?"),
    )
    probs = response_probabilities(history, PERSONAS)
    assert probs == {"Nea Fănică": 0.1, "Mircea Eliade": 0.1, "Robi": 0.5}
