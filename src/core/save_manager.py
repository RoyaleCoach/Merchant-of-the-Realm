"""Save directory and slot management."""

import json
from datetime import datetime
from pathlib import Path

from .config import SAVE_DIR, MAX_SAVE_SLOTS
from .logger import get_logger

log = get_logger(__name__)


def ensure_save_dir() -> Path:
    """Create save directory if it doesn't exist."""
    SAVE_DIR.mkdir(parents=True, exist_ok=True)
    return SAVE_DIR


def list_saves() -> list[dict]:
    """List all save files with metadata."""
    ensure_save_dir()
    saves = []
    for f in sorted(SAVE_DIR.glob("*.json"), reverse=True):
        try:
            data = json.loads(f.read_text())
            saves.append({
                "slot": f.stem,
                "name": data.get("name", "Unknown"),
                "date": data.get("date", "Unknown"),
                "gold": data.get("gold", 0),
                "file": str(f),
            })
        except (json.JSONDecodeError, OSError):
            continue
    return saves


def save_game(slot: str, data: dict) -> Path:
    """Save game data to a slot."""
    ensure_save_dir()
    save_path = SAVE_DIR / f"{slot}.json"
    data["saved_at"] = datetime.now().isoformat()
    save_path.write_text(json.dumps(data, indent=2))
    log.info(f"Game saved to slot '{slot}'")
    return save_path


def load_game(slot: str) -> dict | None:
    """Load game data from a slot."""
    save_path = SAVE_DIR / f"{slot}.json"
    if not save_path.exists():
        log.warning(f"Save slot '{slot}' not found")
        return None
    data = json.loads(save_path.read_text())
    log.info(f"Game loaded from slot '{slot}'")
    return data


def delete_save(slot: str) -> bool:
    """Delete a save slot."""
    save_path = SAVE_DIR / f"{slot}.json"
    if save_path.exists():
        save_path.unlink()
        log.info(f"Save slot '{slot}' deleted")
        return True
    return False
