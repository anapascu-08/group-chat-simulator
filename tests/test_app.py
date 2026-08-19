from fastapi.testclient import TestClient

from app import create_app

PERSONAS = [
    {
        "id": "a-role",
        "name": "A",
        "system_prompt": "sp-a",
        "temperature": 0.5,
        "personality": "haios",
        "bio": "testează lucruri",
        "emoji": "🅰️",
    },
    {
        "id": "b-role",
        "name": "B",
        "system_prompt": "sp-b",
        "temperature": 0.5,
        "personality": "serios",
        "bio": "verifică coduri",
        "emoji": "🅱️",
    },
]


def fake_generate_response(system_prompt, messages, temperature):
    return f"raspuns pentru {system_prompt}"


# rng=0.5 implicit: peste pragul grupului nemenționat (0.2) în testele cu 2
# personas, deci cel nemenționat nu se bagă și selecția rămâne deterministă
# (cel menționat răspunde garantat, nu mai depinde de rng).
def make_client(generate_response=fake_generate_response, personas=None, tmp_path=None, rng=lambda: 0.5):
    app = create_app(
        personas=personas if personas is not None else PERSONAS,
        generate_response=generate_response,
        delay_range=lambda: (0.0, 0.0),
        conversations_dir=tmp_path,
        rng=rng,
    )
    return TestClient(app)


def first_conversation_id(client):
    return client.get("/conversations").json()[0]["id"]


def test_a_conversation_exists_on_startup(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversations = client.get("/conversations").json()
    assert len(conversations) == 1
    assert conversations[0]["message_count"] == 0
    assert conversations[0]["title"] == "Conversație nouă"


def test_messages_starts_empty(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)

    response = client.get(f"/conversations/{conversation_id}/messages")
    assert response.status_code == 200
    assert response.json() == []


def test_chat_adds_human_message(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut tuturor!"})

    messages = client.get(f"/conversations/{conversation_id}/messages").json()
    assert messages[0]["name"] == "Tu"
    assert messages[0]["content"] == "Salut tuturor!"
    assert messages[0]["timestamp"]


def test_chat_triggers_replies_from_all_personas_in_order(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut tuturor!"})

    messages = client.get(f"/conversations/{conversation_id}/messages").json()
    names = [m["name"] for m in messages]
    assert names == ["Tu", "A", "B"]


def test_chat_uses_provided_name(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut!", "name": "Ana"})

    messages = client.get(f"/conversations/{conversation_id}/messages").json()
    assert messages[0]["name"] == "Ana"
    assert messages[0]["content"] == "Salut!"


def test_chat_falls_back_to_default_name_when_missing(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut!"})

    messages = client.get(f"/conversations/{conversation_id}/messages").json()
    assert messages[0]["name"] == "Tu"


def test_chat_falls_back_to_default_name_when_blank(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut!", "name": "   "})

    messages = client.get(f"/conversations/{conversation_id}/messages").json()
    assert messages[0]["name"] == "Tu"


def test_chat_message_timestamp_survives_a_restart(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut!"})

    before_restart = client.get(f"/conversations/{conversation_id}/messages").json()

    restarted_client = make_client(tmp_path=tmp_path)
    after_restart = restarted_client.get(f"/conversations/{conversation_id}/messages").json()

    assert after_restart[0]["timestamp"] == before_restart[0]["timestamp"]


def test_reset_clears_history(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut!"})

    client.post(f"/conversations/{conversation_id}/reset")

    assert client.get(f"/conversations/{conversation_id}/messages").json() == []


def test_chat_with_mention_only_that_persona_replies(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "@A salut!"})

    messages = client.get(f"/conversations/{conversation_id}/messages").json()
    names = [m["name"] for m in messages]
    assert names == ["Tu", "A"]


def test_chat_without_mention_all_personas_reply(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(
        f"/conversations/{conversation_id}/chat",
        json={"message": "Salut tuturor, fără mențiune!"},
    )

    messages = client.get(f"/conversations/{conversation_id}/messages").json()
    names = [m["name"] for m in messages]
    assert names == ["Tu", "A", "B"]


def test_typing_is_none_before_any_chat(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)

    assert client.get(f"/conversations/{conversation_id}/typing").json() == {"name": None}


def test_typing_shows_persona_name_while_generating_and_clears_after(tmp_path):
    captured = []

    def fake_generate_response(system_prompt, messages, temperature):
        captured.append(app.state.internal_state["typing"].get(conversation_id))
        return f"raspuns pentru {system_prompt}"

    app = create_app(
        personas=PERSONAS,
        generate_response=fake_generate_response,
        delay_range=lambda: (0.0, 0.0),
        conversations_dir=tmp_path,
        rng=lambda: 0.5,
    )
    client = TestClient(app)
    conversation_id = first_conversation_id(client)

    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut tuturor!"})

    # fiecare persona a fost surprinsă drept "typing" chiar înainte de generarea ei
    assert captured == ["A", "B"]
    # după ce runda s-a terminat, indicatorul revine la None
    assert client.get(f"/conversations/{conversation_id}/typing").json() == {"name": None}


def test_typing_clears_on_reset(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Salut!"})

    client.post(f"/conversations/{conversation_id}/reset")

    assert client.get(f"/conversations/{conversation_id}/typing").json() == {"name": None}


def test_personas_endpoint_returns_name_and_emoji(tmp_path):
    client = make_client(tmp_path=tmp_path)
    response = client.get("/personas")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "a-role", "name": "A", "emoji": "🅰️", "color": ""},
        {"id": "b-role", "name": "B", "emoji": "🅱️", "color": ""},
    ]


def test_create_conversation_adds_a_new_empty_conversation(tmp_path):
    client = make_client(tmp_path=tmp_path)

    response = client.post("/conversations")
    assert response.status_code == 200
    created = response.json()
    assert created["messages"] == []

    conversations = client.get("/conversations").json()
    assert len(conversations) == 2
    assert any(c["id"] == created["id"] for c in conversations)


def test_conversations_are_independent(tmp_path):
    client = make_client(tmp_path=tmp_path)
    first_id = first_conversation_id(client)
    second_id = client.post("/conversations").json()["id"]

    client.post(f"/conversations/{first_id}/chat", json={"message": "doar in prima"})

    assert len(client.get(f"/conversations/{first_id}/messages").json()) > 0
    assert client.get(f"/conversations/{second_id}/messages").json() == []


def test_messages_for_unknown_conversation_returns_404(tmp_path):
    client = make_client(tmp_path=tmp_path)
    response = client.get("/conversations/nu-exista/messages")
    assert response.status_code == 404


def test_conversation_list_reflects_new_title_after_first_message(tmp_path):
    client = make_client(tmp_path=tmp_path)
    conversation_id = first_conversation_id(client)
    client.post(f"/conversations/{conversation_id}/chat", json={"message": "Primul mesaj aici"})

    conversations = client.get("/conversations").json()
    conv = next(c for c in conversations if c["id"] == conversation_id)
    assert conv["title"] == "Primul mesaj aici"
