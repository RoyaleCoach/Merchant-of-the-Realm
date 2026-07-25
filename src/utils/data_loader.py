"""Load and query JSON data files."""

import json
from pathlib import Path

from src.core.config import DATA_DIR
from src.core.logger import get_logger

log = get_logger(__name__)
_cache: dict[str, dict] = {}


def load_data(filename: str) -> dict:
    """Load a JSON data file from the data directory (cached)."""
    if filename in _cache:
        return _cache[filename]

    path = DATA_DIR / filename
    if not path.exists():
        log.error(f"Data file not found: {path}")
        return {}

    with open(path, "r") as f:
        data = json.load(f)

    _cache[filename] = data
    log.debug(f"Loaded {filename} ({len(data)} entries)")
    return data


def get_item(item_id: str) -> dict | None:
    """Get a single item by ID."""
    items = load_data("items.json")
    return items.get(item_id)


def get_building(building_id: str) -> dict | None:
    """Get a single building by ID."""
    buildings = load_data("buildings.json")
    return buildings.get(building_id)


def get_all_items() -> dict:
    """Get all items."""
    return load_data("items.json")


def get_all_buildings() -> dict:
    """Get all buildings."""
    return load_data("buildings.json")


def get_npc_traits() -> dict:
    """Get NPC generation traits."""
    return load_data("npc_traits.json")
