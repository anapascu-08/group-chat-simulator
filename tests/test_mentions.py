from mentions import mentioned_personas

PERSONAS = [
    {"name": "Nea Fănică"},
    {"name": "Mircea Eliade"},
    {"name": "Robi"},
]


def test_no_mention_returns_all_personas():
    assert mentioned_personas("Salut tuturor!", PERSONAS) == PERSONAS


def test_mention_by_single_word_name():
    assert mentioned_personas("Salut @Robi, ce faci?", PERSONAS) == [PERSONAS[2]]


def test_mention_by_last_word_of_multiword_name():
    assert mentioned_personas("@Fănică ce zici?", PERSONAS) == [PERSONAS[0]]


def test_mention_by_full_name_without_spaces():
    assert mentioned_personas("@NeaFănică ce zici?", PERSONAS) == [PERSONAS[0]]


def test_mention_is_case_insensitive():
    assert mentioned_personas("@robi salut", PERSONAS) == [PERSONAS[2]]


def test_multiple_mentions_preserve_persona_order():
    result = mentioned_personas("@Robi și @Eliade, ce ziceți?", PERSONAS)
    assert result == [PERSONAS[1], PERSONAS[2]]


def test_mention_with_no_matching_persona_returns_none():
    assert mentioned_personas("@cineva salut", PERSONAS) == []


def test_mention_ignores_diacritics():
    assert mentioned_personas("@Fanica ce zici?", PERSONAS) == [PERSONAS[0]]


def test_mention_by_name_prefix():
    assert mentioned_personas("@Mir ce zici?", PERSONAS) == [PERSONAS[1]]
