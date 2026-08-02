"""Event engine — daily events, major events, and player choices."""

import random

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data

log = get_logger(__name__)

# Event history for the current game
_event_log: list[dict] = []


def roll_daily_event(state: GameState) -> tuple[str | None, list[dict]]:
    """
    Roll for a daily random event.
    Returns (message, list of choices) — choices is empty if no player decision.
    """
    events_data = load_data("events.json")
    daily_events = events_data.get("daily", [])

    roll = random.random()
    cumulative = 0.0
    for event in daily_events:
        cumulative += event["chance"]
        if roll <= cumulative:
            _apply_event_effects(state, event["effect"])
            _log_event(state, event["text"], event.get("type", "neutral"))
            return event["text"], []

    return None, []


def roll_major_event(state: GameState) -> tuple[str | None, list[dict]]:
    """
    Roll for a major event (5% daily chance).
    Major events have meaningful consequences and player choices.
    Returns (message, choices) — choices is empty if no event rolled.
    """
    events_data = load_data("events.json")
    major_events = events_data.get("major", [])

    # 5% chance of a major event on any given day
    if random.random() > 0.05:
        return None, []

    event = random.choice(major_events)

    # Apply base effects
    _apply_event_effects(state, event["effect"])

    # Build choices if the event has them
    choices = []
    if "choice" in event:
        for i, opt in enumerate(event["choice"]["options"]):
            choices.append({
                "index": i,
                "label": opt["label"],
                "effect": opt["effect"],
            })

    _log_event(state, event["text"], event.get("type", "neutral"))
    return event["text"], choices


def resolve_choice(state: GameState, choice_effect: dict) -> None:
    """Apply the effects of a player's choice."""
    _apply_event_effects(state, choice_effect)


def _apply_event_effects(state: GameState, effect: dict) -> None:
    """Apply an effect dict to game state."""
    if "gold" in effect:
        state.gold = max(0, state.gold + effect["gold"])
    if "mood" in effect:
        # Mood affects happiness
        state.happiness = max(0, min(100, state.happiness + effect["mood"]))
    if "happiness" in effect:
        state.happiness = max(0, min(100, state.happiness + effect["happiness"]))
    if "crime" in effect:
        state.crime = max(0, min(100, state.crime + effect["crime"]))
    if "population" in effect:
        state.population = max(0, state.population + effect["population"])


def _log_event(state: GameState, text: str, event_type: str) -> None:
    """Add an event to the log."""
    _event_log.append({
        "text": text,
        "type": event_type,
        "day": state.total_days,
        "date": state.date_string,
        "season": state.season,
    })


def get_event_log(limit: int = 20) -> list[dict]:
    """Get recent events from the log."""
    return _event_log[-limit:]


def clear_event_log() -> None:
    """Clear the event log (e.g., on new game)."""
    _event_log.clear()


def get_event_summary() -> dict:
    """Get summary statistics of events."""
    if not _event_log:
        return {"total": 0, "positive": 0, "negative": 0, "neutral": 0}

    counts = {"positive": 0, "negative": 0, "neutral": 0, "disaster": 0, "opportunity": 0}
    for e in _event_log:
        t = e.get("type", "neutral")
        if t in counts:
            counts[t] += 1
        else:
            counts["neutral"] += 1

    return {"total": len(_event_log), **counts}
