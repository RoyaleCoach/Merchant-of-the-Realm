"""Tick system — advances time and triggers daily updates."""

from src.core.game_state import GameState
from src.core.logger import get_logger

log = get_logger(__name__)


def tick(state: GameState) -> list[str]:
    """
    Advance the game by one day.
    Returns a list of event messages that occurred.
    """
    messages = []
    state.advance_day()
    log.info(f"Tick: {state.date_string}")

    # Daily updates happen here (will be expanded in later phases)
    # Phase 2+: economy update, production, NPC behavior, events, weather
    messages.append(f"--- {state.date_string} ---")

    return messages
