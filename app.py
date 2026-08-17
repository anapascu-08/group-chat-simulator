"""Backend FastAPI peste aceeași logică de conversație/orchestrare din CLI."""

import random
import time
from pathlib import Path
from typing import Callable, Optional, Union

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from config import HUMAN_NAME, get_delay_range_seconds
from conversation import Conversation
from conversation_store import ConversationNotFound, ConversationStore
from ollama_client import generate_response as _default_generate_response
from orchestrator import respond_as
from personas_store import load_personas
from responders import select_responders


STATIC_DIR = Path(__file__).parent / "static"
CONVERSATIONS_DIR = Path(__file__).parent / "conversations"


class ChatRequest(BaseModel):
    message: str
    name: Optional[str] = None


def create_app(
    personas: Optional[list] = None,
    generate_response: Callable = _default_generate_response,
    delay_range: Callable = get_delay_range_seconds,
    conversations_dir: Union[str, Path] = CONVERSATIONS_DIR,
    rng: Callable = random.random,
) -> FastAPI:
    app = FastAPI(title="Group Chat Simulator")
    store = ConversationStore(conversations_dir)
    conversations: dict[str, Conversation] = {}
    state = {
        "personas": personas if personas is not None else load_personas(),
        "round_ids": {},
        "typing": {},
    }
    app.state.internal_state = state  # hook pentru teste — inspecție directă, fără round-trip HTTP

    if not store.list_conversations():
        store.create()

    def get_conversation(conversation_id: str) -> Conversation:
        if conversation_id not in conversations:
            try:
                history = store.load_messages(conversation_id)
            except ConversationNotFound:
                raise HTTPException(status_code=404, detail="Conversație inexistentă")
            conversations[conversation_id] = Conversation(history)
        return conversations[conversation_id]

    def generate_round(conversation_id: str, round_id: int, personas: list, target_message: dict) -> None:
        conversation = conversations[conversation_id]
        for persona in personas:
            time.sleep(random.uniform(*delay_range()))
            if round_id != state["round_ids"].get(conversation_id):
                state["typing"][conversation_id] = None
                return  # a venit un mesaj nou/reset între timp, runda asta nu mai e validă
            state["typing"][conversation_id] = persona["name"]
            reply = respond_as(conversation, persona, target_message=target_message, generate_response=generate_response)
            state["typing"][conversation_id] = None
            store.append_message(conversation_id, persona["name"], reply)

    @app.get("/conversations")
    def list_conversations():
        return store.list_conversations()

    @app.post("/conversations")
    def create_conversation():
        data = store.create()
        conversations[data["id"]] = Conversation()
        return data

    @app.get("/conversations/{conversation_id}/messages")
    def get_messages(conversation_id: str):
        return get_conversation(conversation_id).get_history()

    @app.get("/conversations/{conversation_id}/typing")
    def get_typing(conversation_id: str):
        return {"name": state["typing"].get(conversation_id)}

    @app.post("/conversations/{conversation_id}/chat")
    def post_chat(conversation_id: str, payload: ChatRequest, background_tasks: BackgroundTasks):
        conversation = get_conversation(conversation_id)
        sender = payload.name.strip() if payload.name and payload.name.strip() else HUMAN_NAME
        conversation.add_message(sender, payload.message)
        store.append_message(conversation_id, sender, payload.message)

        round_id = state["round_ids"].get(conversation_id, 0) + 1
        state["round_ids"][conversation_id] = round_id
        targets = select_responders(conversation.get_history(), state["personas"], rng=rng)
        target_message = {"name": sender, "content": payload.message}
        background_tasks.add_task(generate_round, conversation_id, round_id, targets, target_message)
        return {"status": "ok"}

    @app.post("/conversations/{conversation_id}/reset")
    def post_reset(conversation_id: str):
        conversation = get_conversation(conversation_id)
        conversation.reset()
        store.reset(conversation_id)
        state["round_ids"][conversation_id] = state["round_ids"].get(conversation_id, 0) + 1
        state["typing"][conversation_id] = None
        return {"status": "ok"}

    @app.get("/personas")
    def get_personas():
        return [
            {"id": p.get("id", ""), "name": p["name"], "emoji": p.get("emoji", ""), "color": p.get("color", "")}
            for p in state["personas"]
        ]

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

    return app


app = create_app()
