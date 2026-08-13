"""Istoric de conversație în memorie, pentru un singur grup chat."""


class Conversation:
    def __init__(self, history: list = None):
        self._history = list(history) if history else []

    def add_message(self, name: str, content: str) -> None:
        self._history.append({"name": name, "content": content})

    def get_history(self) -> list[dict]:
        return list(self._history)

    def reset(self) -> None:
        self._history.clear()

    def messages_for(self, persona_name: str) -> list[dict]:
        """Istoricul din perspectiva unei persona.

        Propriile mesaje ale personei devin "assistant"; toate celelalte
        (userul uman sau alte personas) devin "user", prefixate cu numele
        vorbitorului, ca personajul curent să știe cine a zis ce.
        """
        messages = []
        for msg in self._history:
            if msg["name"] == persona_name:
                messages.append({"role": "assistant", "content": msg["content"]})
            else:
                messages.append(
                    {"role": "user", "content": f"{msg['name']}: {msg['content']}"}
                )
        return messages
