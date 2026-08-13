"""Persistență JSON per conversație: fiecare conversație e un fișier propriu
într-un director, ca istoricul să supraviețuiască unui restart de server."""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Union

DEFAULT_DIR = "conversations"
TITLE_MAX_LEN = 40
DEFAULT_TITLE = "Conversație nouă"


class ConversationNotFound(Exception):
    pass


class ConversationStore:
    def __init__(self, directory: Union[str, Path] = DEFAULT_DIR):
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)

    def create(self) -> dict:
        data = {
            "id": uuid.uuid4().hex,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "messages": [],
        }
        self._write(data)
        return data

    def list_conversations(self) -> list[dict]:
        summaries = [self._summarize(self._read_path(p)) for p in self._dir.glob("*.json")]
        summaries.sort(key=lambda s: s["created_at"], reverse=True)
        return summaries

    def load_messages(self, conversation_id: str) -> list[dict]:
        return self._read(conversation_id)["messages"]

    def exists(self, conversation_id: str) -> bool:
        return self._path(conversation_id).exists()

    def append_message(self, conversation_id: str, name: str, content: str) -> None:
        data = self._read(conversation_id)
        data["messages"].append({"name": name, "content": content})
        self._write(data)

    def reset(self, conversation_id: str) -> None:
        data = self._read(conversation_id)
        data["messages"] = []
        self._write(data)

    def _summarize(self, data: dict) -> dict:
        return {
            "id": data["id"],
            "created_at": data["created_at"],
            "title": self._title_for(data),
            "message_count": len(data["messages"]),
        }

    @staticmethod
    def _title_for(data: dict) -> str:
        for msg in data["messages"]:
            content = msg["content"].strip()
            if content:
                return content[:TITLE_MAX_LEN]
        return DEFAULT_TITLE

    def _path(self, conversation_id: str) -> Path:
        return self._dir / f"{conversation_id}.json"

    def _read(self, conversation_id: str) -> dict:
        return self._read_path(self._path(conversation_id))

    def _read_path(self, path: Path) -> dict:
        if not path.exists():
            raise ConversationNotFound(path.stem)
        return json.loads(path.read_text(encoding="utf-8"))

    def _write(self, data: dict) -> None:
        self._path(data["id"]).write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
