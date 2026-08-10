"""Backend FastAPI peste aceeași logică de conversație/orchestrare din CLI."""

import random
import time
from typing import Callable, Optional

from fastapi import BackgroundTasks, FastAPI
from pydantic import BaseModel

from config import HUMAN_NAME, get_delay_range_seconds
from conversation import Conversation
from ollama_client import generate_response as _default_generate_response
from orchestrator import respond_as
from personas_store import load_personas


class ChatRequest(BaseModel):
    message: str


def create_app(
    personas: Optional[list] = None,
    generate_response: Callable = _default_generate_response,
    delay_range: Callable = get_delay_range_seconds,
) -> FastAPI:
    app = FastAPI(title="Group Chat Simulator")
    conversation = Conversation()
    state = {
        "personas": personas if personas is not None else load_personas(),
        "round_id": 0,
    }

    def generate_round(round_id: int) -> None:
        for persona in state["personas"]:
            time.sleep(random.uniform(*delay_range()))
            if round_id != state["round_id"]:
                return  # a venit un /reset între timp, runda asta nu mai e validă
            respond_as(conversation, persona, generate_response=generate_response)

    @app.post("/chat")
    def post_chat(payload: ChatRequest, background_tasks: BackgroundTasks):
        conversation.add_message(HUMAN_NAME, payload.message)
        state["round_id"] += 1
        background_tasks.add_task(generate_round, state["round_id"])
        return {"status": "ok"}

    @app.get("/messages")
    def get_messages():
        return conversation.get_history()

    @app.post("/reset")
    def post_reset():
        conversation.reset()
        state["round_id"] += 1
        return {"status": "ok"}

    return app


app = create_app()
