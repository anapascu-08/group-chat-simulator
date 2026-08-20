from mentions import mentioned_personas, strip_self_mentions

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


def test_strip_self_mentions_removes_at_symbol_from_own_name():
    assert strip_self_mentions("@Robi zice că-i mișto!", PERSONAS[2]) == "Robi zice că-i mișto!"


def test_strip_self_mentions_matches_prefix_and_no_space_form():
    assert strip_self_mentions("@Fănică e de acord cu asta.", PERSONAS[0]) == "Fănică e de acord cu asta."
    assert strip_self_mentions("@NeaFănică e de acord.", PERSONAS[0]) == "NeaFănică e de acord."


def test_strip_self_mentions_ignores_diacritics_and_case():
    assert strip_self_mentions("@fanica zice mersi", PERSONAS[0]) == "fanica zice mersi"


def test_strip_self_mentions_leaves_mentions_of_others_untouched():
    assert strip_self_mentions("@Robi ce zici?", PERSONAS[0]) == "@Robi ce zici?"


def test_strip_self_mentions_leaves_text_without_mentions_untouched():
    assert strip_self_mentions("Nicio mențiune aici.", PERSONAS[2]) == "Nicio mențiune aici."


def test_strip_self_mentions_matches_alias_used_in_own_system_prompt():
    # ex. Cântărețul Nae se prezintă "Nea Nae" în system_prompt — un nickname
    # diferit de "name" — deci trebuie recunoscut și el ca auto-mențiune.
    persona = {"name": "Cântărețul Nae", "aliases": ["Nea Nae"]}
    assert strip_self_mentions("@NeaNae, hooo, las-o balta!", persona) == "NeaNae, hooo, las-o balta!"
    assert strip_self_mentions("@Nea zice să mai treci pe la noi!", persona) == "Nea zice să mai treci pe la noi!"


def test_mentioned_personas_also_matches_alias():
    persona = {"name": "Cântărețul Nae", "aliases": ["Nea Nae"]}
    assert mentioned_personas("@NeaNae ce mai cânți?", [persona]) == [persona]
