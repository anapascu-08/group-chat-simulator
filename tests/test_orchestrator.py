from conversation import Conversation
from orchestrator import FALLBACK_REPLY, humanize, respond_as


def test_respond_as_adds_reply_to_conversation():
    conv = Conversation()
    conv.add_message("Tu", "Salut tuturor!")
    persona = {"name": "Nea Fănică", "system_prompt": "sp", "temperature": 0.9}

    reply = respond_as(conv, persona, generate_response=lambda **kwargs: "Bună, mă!")

    assert reply == "Bună, mă!"
    last = conv.get_history()[-1]
    assert last["name"] == "Nea Fănică"
    assert last["content"] == "Bună, mă!"
    assert last["timestamp"]


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

    target_message = {"name": "Tu", "content": "Salut!"}
    respond_as(conv, persona, target_message=target_message, generate_response=fake_generate)

    assert captured["system_prompt"].startswith("sp-fanica")
    assert "subiect" in captured["system_prompt"].lower()
    assert captured["temperature"] == 0.5
    assert captured["messages"] == [{"role": "user", "content": "Tu: Salut!"}]


def test_target_message_stays_anchored_across_round():
    """Regresie: a doua persona din rundă trebuie să răspundă tot la
    întrebarea inițială a utilizatorului, nu la replica primei persona."""
    conv = Conversation()
    conv.add_message("Tu", "Ce mai faceți?")
    target_message = {"name": "Tu", "content": "Ce mai faceți?"}

    persona_a = {"name": "A", "system_prompt": "sp-a", "temperature": 0.5}
    persona_b = {"name": "B", "system_prompt": "sp-b", "temperature": 0.5}

    respond_as(conv, persona_a, target_message=target_message, generate_response=lambda **kwargs: "Bine, mersi!")

    captured = {}

    def fake_generate_b(system_prompt, messages, temperature):
        captured["system_prompt"] = system_prompt
        return "Și eu bine!"

    respond_as(conv, persona_b, target_message=target_message, generate_response=fake_generate_b)

    assert "Ce mai faceți?" in captured["system_prompt"]
    assert "Bine, mersi!" not in captured["system_prompt"]


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


def test_respond_as_falls_back_when_generate_response_always_raises():
    """Dacă Ollama nu răspunde (ex. serviciul e oprit), respond_as nu trebuie
    să propage excepția — altfel indicatorul "X scrie..." rămâne blocat
    pentru totdeauna, fiindcă linia care îl resetează în app.py nu se mai
    execută."""
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    persona = {"name": "A", "system_prompt": "sp", "temperature": 0.5}

    def broken_generate(system_prompt, messages, temperature):
        raise ConnectionError("Ollama nu răspunde")

    reply = respond_as(conv, persona, generate_response=broken_generate)

    assert reply == FALLBACK_REPLY
    assert conv.get_history()[-1]["content"] == FALLBACK_REPLY


def test_respond_as_retries_after_a_transient_exception():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    persona = {"name": "A", "system_prompt": "sp", "temperature": 0.5}
    calls = []

    def flaky_generate(system_prompt, messages, temperature):
        calls.append(1)
        if len(calls) == 1:
            raise ConnectionError("timeout trecător")
        return "Salut și eu!"

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


def test_humanize_strips_bold_markers():
    assert humanize("Salut **prietene**, ce faci?") == "Salut prietene, ce faci?"


def test_humanize_strips_headers():
    assert humanize("# Salut\nCe faci?") == "Salut\nCe faci?"


def test_humanize_strips_bullet_markers():
    assert humanize("- primul\n- al doilea") == "primul\nal doilea"


def test_humanize_strips_backticks():
    assert humanize("Ascultă `muzica` asta") == "Ascultă muzica asta"


def test_respond_as_humanizes_reply_before_storing():
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    persona = {"name": "A", "system_prompt": "sp", "temperature": 0.5}

    reply = respond_as(conv, persona, generate_response=lambda **kwargs: "**Salut** prietene!")

    assert reply == "Salut prietene!"
    assert conv.get_history()[-1]["content"] == "Salut prietene!"


def test_respond_as_strips_self_mention_before_storing():
    """Regresie: modelul mai taguiește din obicei propriul nume — nu are ce
    căuta o persona taguită pe ea însăși în chat."""
    conv = Conversation()
    conv.add_message("Tu", "Salut!")
    persona = {"name": "Nea Fănică", "system_prompt": "sp", "temperature": 0.5}

    reply = respond_as(conv, persona, generate_response=lambda **kwargs: "@Fănică zice hooo, măi!")

    assert reply == "Fănică zice hooo, măi!"
    assert conv.get_history()[-1]["content"] == "Fănică zice hooo, măi!"
