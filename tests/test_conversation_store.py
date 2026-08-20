import pytest

from conversation_store import ConversationNotFound, ConversationStore


def test_create_returns_conversation_with_empty_history(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()
    assert data["messages"] == []
    assert data["id"]
    assert data["created_at"]


def test_create_persists_a_file_on_disk(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()
    assert (tmp_path / f"{data['id']}.json").exists()


def test_list_is_empty_when_no_conversations_exist(tmp_path):
    store = ConversationStore(tmp_path)
    assert store.list_conversations() == []


def test_list_returns_a_summary_of_each_conversation(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()

    summaries = store.list_conversations()

    assert len(summaries) == 1
    assert summaries[0]["id"] == data["id"]
    assert summaries[0]["message_count"] == 0
    assert summaries[0]["title"] == "Conversație nouă"


def test_list_orders_most_recently_created_first(tmp_path):
    store = ConversationStore(tmp_path)
    first = store.create()
    second = store.create()

    ids = [s["id"] for s in store.list_conversations()]

    assert ids == [second["id"], first["id"]]


def test_append_message_persists_it(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()

    store.append_message(data["id"], "Tu", "Salut!", timestamp="2024-01-01T10:00:00+00:00")

    assert store.load_messages(data["id"]) == [
        {"name": "Tu", "content": "Salut!", "timestamp": "2024-01-01T10:00:00+00:00"}
    ]


def test_append_message_generates_a_timestamp_when_not_given(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()

    store.append_message(data["id"], "Tu", "Salut!")

    assert store.load_messages(data["id"])[0]["timestamp"]


def test_list_title_uses_first_non_empty_message(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()

    message = "Salut tuturor, ce mai faceți azi pe-aici?"
    store.append_message(data["id"], "Tu", message)

    summaries = store.list_conversations()
    assert summaries[0]["title"] == message
    assert summaries[0]["message_count"] == 1


def test_list_title_keeps_long_message_in_full(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()

    message = "Ați văzut ultimele știri? Ce părere aveți despre asta?"
    store.append_message(data["id"], "Tu", message)

    summaries = store.list_conversations()
    assert summaries[0]["title"] == message


def test_rename_overrides_the_derived_title(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()
    store.append_message(data["id"], "Tu", "Salut tuturor")

    store.rename(data["id"], "Titlu ales de mine")

    summaries = store.list_conversations()
    assert summaries[0]["title"] == "Titlu ales de mine"


def test_rename_with_blank_title_reverts_to_derived_title(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()
    store.append_message(data["id"], "Tu", "Salut tuturor")
    store.rename(data["id"], "Titlu ales de mine")

    store.rename(data["id"], "   ")

    summaries = store.list_conversations()
    assert summaries[0]["title"] == "Salut tuturor"


def test_rename_raises_for_unknown_id(tmp_path):
    store = ConversationStore(tmp_path)
    with pytest.raises(ConversationNotFound):
        store.rename("nu-exista", "Titlu nou")


def test_reset_clears_persisted_messages(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()
    store.append_message(data["id"], "Tu", "Salut!")

    store.reset(data["id"])

    assert store.load_messages(data["id"]) == []


def test_exists_true_for_known_id_false_otherwise(tmp_path):
    store = ConversationStore(tmp_path)
    data = store.create()

    assert store.exists(data["id"]) is True
    assert store.exists("nu-exista") is False


def test_load_messages_raises_for_unknown_id(tmp_path):
    store = ConversationStore(tmp_path)
    with pytest.raises(ConversationNotFound):
        store.load_messages("nu-exista")


def test_directory_is_created_if_missing(tmp_path):
    directory = tmp_path / "nested" / "conversations"
    store = ConversationStore(directory)
    store.create()
    assert directory.exists()
