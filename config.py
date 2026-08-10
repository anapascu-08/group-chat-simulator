"""Config citit din environment, cu valori implicite potrivite pentru dezvoltare."""

import os

from dotenv import load_dotenv

load_dotenv()

HUMAN_NAME = "Tu"


def get_delay_range_seconds() -> tuple[float, float]:
    """Interval (min, max) de delay simulat între răspunsurile personas.

    Implicit foarte mic (0.5-1.5s), ca să vezi răspunsurile rapid în dev.
    Pentru demo, setează RESPONSE_DELAY_MIN_S=120 RESPONSE_DELAY_MAX_S=480
    (2-8 minute), conform SPEC.md.
    """
    min_s = float(os.environ.get("RESPONSE_DELAY_MIN_S", "0.5"))
    max_s = float(os.environ.get("RESPONSE_DELAY_MAX_S", "1.5"))
    return min_s, max_s
