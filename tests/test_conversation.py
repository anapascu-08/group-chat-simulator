from conversation import Conversation


def test_starts_empty():
    conv = Conversation()
    assert conv.get_history() == []


def test_add_message_appends_to_history():
    conv = Conversation()
    conv.add_message("Tu", "Salut!", timestamp="2024-01-01T10:00:00+00:00")
    assert conv.get_history() == [
        {"name": "Tu", "content": "Salut!", "timestamp": "2024-01-01T10:00:00+00:00"}
    ]


def test_add_message_generates_a_timestamp_when_not_given():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    assert conv.get_history()[0]["timestamp"]


def test_reset_clears_history():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    conv.reset()
    assert conv.get_history() == []


def test_get_history_returns_a_copy():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    history = conv.get_history()
    history.append({"name": "altcineva", "content": "intrus"})
    assert len(conv.get_history()) == 1


def test_messages_for_marks_own_messages_as_assistant():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    conv.add_message("Nea Fănică", "Bună, mă!")

    messages = conv.messages_for("Nea Fănică")

    assert messages == [
        {"role": "user", "content": "Tu: Salut!"},
        {"role": "assistant", "content": "Bună, mă!"},
    ]


def test_messages_for_prefixes_other_personas_with_name():
    conv = Conversation()
    conv.add_message("Robi", "Ce facem, frate?")

    messages = conv.messages_for("Nea Fănică")

    assert messages == [{"role": "user", "content": "Robi: Ce facem, frate?"}]
