"""One-off: completează timestamp-ul mesajelor mai vechi, salvate înainte ca
acest câmp să existe. Fiecare mesaj fără timestamp primește created_at al
conversației + un offset de câteva secunde per poziție, ca ordinea și
separatorii de zi din UI să funcționeze corect.

Rulare: python scripts/backfill_timestamps.py [--dry-run]
"""

import argparse
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

CONVERSATIONS_DIR = Path(__file__).resolve().parent.parent / "conversations"
SECONDS_PER_MESSAGE = 5


def backfill(data: dict) -> int:
    created_at = datetime.fromisoformat(data["created_at"])
    filled = 0
    for i, msg in enumerate(data["messages"]):
        if not msg.get("timestamp"):
            msg["timestamp"] = (created_at + timedelta(seconds=i * SECONDS_PER_MESSAGE)).isoformat()
            filled += 1
    return filled


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="doar afișează ce s-ar schimba")
    args = parser.parse_args()

    if not CONVERSATIONS_DIR.exists():
        print(f"Directorul {CONVERSATIONS_DIR} nu există.", file=sys.stderr)
        sys.exit(1)

    total_files = 0
    total_filled = 0
    for path in sorted(CONVERSATIONS_DIR.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        filled = backfill(data)
        if filled:
            total_files += 1
            total_filled += filled
            print(f"{path.name}: {filled} mesaje completate")
            if not args.dry_run:
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    mode = "(dry-run, nimic scris)" if args.dry_run else "(scris pe disc)"
    print(f"\nTotal: {total_filled} mesaje în {total_files} conversații {mode}")


if __name__ == "__main__":
    main()
