from responders import select_responders

PERSONAS = [
    {"name": "Nea Fănică", "personality": "haios, jovial, vorbește în metafore", "bio": "Cântăreț de muzică populară"},
    {
        "name": "Mircea Eliade",
        "personality": "erudit, filosofic, vorbește despre mit, sacru și istoria religiilor",
        "bio": "Istoric al religiilor, filozof și scriitor",
    },
    {"name": "Robi", "personality": "descurcăreț, vorbește în șpagă, mereu cu ochii pe un ban în plus", "bio": "Un smecheraș care vrea să facă și el un ban"},
]


def test_explicit_mention_takes_priority_over_relevance():
    # mesajul e tematic relevant pentru Eliade (religie), dar @Robi e explicit
    result = select_responders("@Robi ce zici de religie?", PERSONAS)
    assert result == [PERSONAS[2]]


def test_no_mention_falls_back_to_relevance():
    result = select_responders("Ce ziceți despre mit și religie?", PERSONAS)
    assert result == [PERSONAS[1]]


def test_no_mention_and_no_relevance_match_returns_all():
    result = select_responders("Ce faceți diseară?", PERSONAS)
    assert result == PERSONAS


def test_mention_matching_nobody_returns_none_even_if_topic_is_relevant():
    result = select_responders("@cineva ce zici de religie?", PERSONAS)
    assert result == []
