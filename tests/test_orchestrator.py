from conversation import Conversation
from orchestrator import FALLBACK_REPLY, respond_as


def test_respond_as_adds_reply_to_conversation():
    conv = Conversation()
    conv.add_message("Tu", "Salut tuturor!")
    persona = {"name": "Nea Fănică", "system_prompt": "sp", "temperature": 0.9}

    reply = respond_as(conv, persona, generate_response=lambda **kwargs: "Bună, mă!")

    assert reply == "Bună, mă!"
    assert conv.get_history()[-1] == {"name": "Nea Fănică", "content": "Bună, mă!"}


def test_respond_as_passes_persona_system_prompt_and_temperature():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    persona = {"name": "Nea Fănică", "system_prompt": "sp-fanica", "temperature": 0.5}
    captured = {}

    def fake_generate(system_prompt, messages, temperature):
        captured["system_prompt"] = system_prompt
        captured["messages"] = messages
        captured["temperature"] = temperature
        return "ok"

    respond_as(conv, persona, generate_response=fake_generate)

    assert captured["system_prompt"].startswith("sp-fanica")
    assert "subiect" in captured["system_prompt"].lower()
    assert captured["temperature"] == 0.5
    assert captured["messages"] == [{"role": "user", "content": "Tu: Salut!"}]


def test_later_persona_sees_earlier_persona_reply_same_round():
    conv = Conversation()
    conv.add_message("Tu", "Salut tuturor!")

    persona_a = {"name": "A", "system_prompt": "sp-a", "temperature": 0.5}
    persona_b = {"name": "B", "system_prompt": "sp-b", "temperature": 0.5}

    respond_as(conv, persona_a, generate_response=lambda **kwargs: "Salut, sunt A!")

    captured = {}

    def fake_generate_b(system_prompt, messages, temperature):
        captured["messages"] = messages
        return "Salut, sunt B!"

    respond_as(conv, persona_b, generate_response=fake_generate_b)

    assert {"role": "user", "content": "A: Salut, sunt A!"} in captured["messages"]


def test_respond_as_retries_once_when_reply_is_empty():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    persona = {"name": "A", "system_prompt": "sp", "temperature": 0.5}
    calls = []

    def flaky_generate(system_prompt, messages, temperature):
        calls.append(1)
        return "" if len(calls) == 1 else "Salut și eu!"

    reply = respond_as(conv, persona, generate_response=flaky_generate)

    assert reply == "Salut și eu!"
    assert len(calls) == 2


def test_respond_as_falls_back_when_still_empty_after_retry():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    persona = {"name": "A", "system_prompt": "sp", "temperature": 0.5}

    reply = respond_as(conv, persona, generate_response=lambda **kwargs: "   ")

    assert reply == FALLBACK_REPLY
    assert conv.get_history()[-1]["content"] == FALLBACK_REPLY
