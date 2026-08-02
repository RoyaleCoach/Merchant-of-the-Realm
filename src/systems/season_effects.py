"""Season effects engine — applies seasonal production modifiers and events."""

import random

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data

log = get_logger(__name__)


def get_season_data(season: str) -> dict:
    """Get season metadata (icon, description, modifiers)."""
    data = load_data("season_effects.json")
    return data["seasons"].get(season, {})


def get_season_modifier(season: str, category: str) -> float:
    """Get the production multiplier for a category in a given season."""
    season_data = get_season_data(season)
    modifiers = season_data.get("modifiers", {})
    return modifiers.get(category, 1.0)


def get_season_icon(season: str) -> str:
    """Get the icon for a season."""
    return get_season_data(season).get("icon", "")


def get_season_description(season: str) -> str:
    """Get the flavor description for a season."""
    return get_season_data(season).get("description", "")


def compute_effective_mod(state: GameState, category: str, base_mod: float) -> float:
    """
    Compute the effective production modifier combining weather and season.
    Result = weather_mod * season_mod
    """
    season_mod = get_season_modifier(state.season, category)
    return base_mod * season_mod


def get_active_effects(state: GameState) -> list[dict]:
    """
    Return a list of all active effects for the current season and weather.
    Each effect has: type, name, icon, description, modifier
    """
    effects = []

    # Season effect
    season_data = get_season_data(state.season)
    if season_data:
        effects.append({
            "type": "season",
            "name": state.season,
            "icon": season_data.get("icon", ""),
            "description": season_data.get("description", ""),
            "modifiers": season_data.get("modifiers", {}),
        })

    # Weather effect
    weather_data = load_data("weather.json")
    for wt in weather_data.get("types", []):
        if wt["name"] == state.weather:
            effects.append({
                "type": "weather",
                "name": state.weather,
                "icon": wt.get("icon", ""),
                "description": _weather_effect_description(wt),
                "production_mod": wt.get("production_mod", 1.0),
                "mood_mod": wt.get("mood_mod", 0),
            })
            break

    return effects


def roll_season_event(state: GameState) -> str | None:
    """Roll for a random seasonal flavor event. Returns message or None."""
    season_data = get_season_data(state.season)
    events = season_data.get("events", [])
    if not events:
        return None

    # 40% chance of a seasonal flavor event on season start
    if random.random() > 0.4:
        return None

    return f"{get_season_icon(state.season)} {random.choice(events)}"


def _weather_effect_description(weather_type: dict) -> str:
    """Generate a human-readable description of weather effects."""
    prod = weather_type.get("production_mod", 1.0)
    mood = weather_type.get("mood_mod", 0)

    parts = []
    if prod > 1.0:
        parts.append(f"Production +{int((prod - 1) * 100)}%")
    elif prod < 1.0:
        parts.append(f"Production {int((prod - 1) * 100)}%")

    if mood > 0:
        parts.append(f"Mood +{mood}")
    elif mood < 0:
        parts.append(f"Mood {mood}")

    return ", ".join(parts) if parts else "No special effects"


def get_category_for_item(state: GameState, item_id: str) -> str:
    """Look up the category of an item from market data."""
    for item in state.market:
        if item["item_id"] == item_id:
            return item.get("category", "general")
    return "general"
