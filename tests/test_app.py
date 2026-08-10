from fastapi.testclient import TestClient

from app import create_app

PERSONAS = [
    {"name": "A", "system_prompt": "sp-a", "temperature": 0.5},
    {"name": "B", "system_prompt": "sp-b", "temperature": 0.5},
]


def fake_generate_response(system_prompt, messages, temperature):
    return f"raspuns pentru {system_prompt}"


def make_client(generate_response=fake_generate_response, personas=None):
    app = create_app(
        personas=personas if personas is not None else PERSONAS,
        generate_response=generate_response,
        delay_range=lambda: (0.0, 0.0),
    )
    return TestClient(app)


def test_messages_starts_empty():
    client = make_client()
    response = client.get("/messages")
    assert response.status_code == 200
    assert response.json() == []


def test_chat_adds_human_message():
    client = make_client()
    client.post("/chat", json={"message": "Salut tuturor!"})

    messages = client.get("/messages").json()
    assert messages[0] == {"name": "Tu", "content": "Salut tuturor!"}


def test_chat_triggers_replies_from_all_personas_in_order():
    client = make_client()
    client.post("/chat", json={"message": "Salut tuturor!"})

    messages = client.get("/messages").json()
    names = [m["name"] for m in messages]
    assert names == ["Tu", "A", "B"]


def test_chat_uses_provided_name():
    client = make_client()
    client.post("/chat", json={"message": "Salut!", "name": "Ana"})

    messages = client.get("/messages").json()
    assert messages[0] == {"name": "Ana", "content": "Salut!"}


def test_chat_falls_back_to_default_name_when_missing():
    client = make_client()
    client.post("/chat", json={"message": "Salut!"})

    messages = client.get("/messages").json()
    assert messages[0]["name"] == "Tu"


def test_chat_falls_back_to_default_name_when_blank():
    client = make_client()
    client.post("/chat", json={"message": "Salut!", "name": "   "})

    messages = client.get("/messages").json()
    assert messages[0]["name"] == "Tu"


def test_reset_clears_history():
    client = make_client()
    client.post("/chat", json={"message": "Salut!"})

    client.post("/reset")

    assert client.get("/messages").json() == []
