"""Chat loop în terminal: toate personas răspund pe rând, cu delay simulat."""

import random
import time

from config import HUMAN_NAME, get_delay_range_seconds
from conversation import Conversation
from orchestrator import respond_as
from personas_store import load_personas

RESET_COMMAND = "/reset"


def main() -> None:
    personas = load_personas()
    conversation = Conversation()

    print(f"Group Chat Simulator — personas: {', '.join(p['name'] for p in personas)}")
    print(f"Scrie un mesaj și apasă Enter. '{RESET_COMMAND}' golește conversația. Ctrl+C pentru ieșire.\n")

    while True:
        try:
            user_message = input(f"{HUMAN_NAME}: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nLa revedere!")
            break

        if not user_message:
            continue

        if user_message == RESET_COMMAND:
            conversation.reset()
            print("(conversație resetată)\n")
            continue

        conversation.add_message(HUMAN_NAME, user_message)

        for persona in personas:
            time.sleep(random.uniform(*get_delay_range_seconds()))
            reply = respond_as(conversation, persona)
            print(f"{persona['name']}: {reply}\n")


if __name__ == "__main__":
    main()
