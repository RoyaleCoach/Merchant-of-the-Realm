"""Tick system — advances time and triggers all daily updates."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.systems.daily_updates import (
    update_economy,
    update_production,
    update_npcs,
    update_weather,
    roll_events,
    is_season_start,
    roll_seasonal_events,
    get_weather_mod,
    get_mood_mod,
)
from src.systems.season_effects import roll_season_event
from src.systems.workforce import pay_workers, update_worker_stats
from src.systems.citizens import process_daily_citizens

log = get_logger(__name__)


def tick(state: GameState) -> list[str]:
    """
    Advance the game by one day.
    Triggers: economy, production, NPC behavior, weather, events.
    Returns a list of event messages that occurred.
    """
    messages = []

    # Advance the calendar
    state.advance_day()
    messages.append(f"--- {state.date_string} ---")

    # Seasonal events (first day of season)
    if is_season_start(state):
        seasonal = roll_seasonal_events(state)
        messages.extend(seasonal)
        # Flavor event from season effects
        flavor = roll_season_event(state)
        if flavor:
            messages.append(flavor)

    # Weather update
    weather_msg = update_weather(state)
    if weather_msg:
        messages.append(weather_msg)

    # Get current conditions
    weather_mod = get_weather_mod(state)
    mood_mod = get_mood_mod(state)

    # Daily random events
    event_msgs = roll_events(state)
    messages.extend(event_msgs)

    # Production (buildings produce/consume goods)
    prod_msgs = update_production(state, weather_mod)
    messages.extend(prod_msgs)

    # Economy (price recalculation)
    econ_msgs = update_economy(state, weather_mod)
    messages.extend(econ_msgs)

    # Citizen simulation (consumption, happiness, crime, migration)
    citizen_msgs = process_daily_citizens(state)
    messages.extend(citizen_msgs)

    # NPC behavior
    update_npcs(state, mood_mod)

    # Worker stat updates (morale, health, experience)
    update_worker_stats(state)

    # Payroll — pay workers their daily wages
    amount_paid, payroll_msg = pay_workers(state)
    if amount_paid > 0:
        messages.append(payroll_msg)
    else:
        messages.append(payroll_msg)  # includes warning if unpaid

    log.info(f"Tick: {state.date_string} | Weather: {state.weather} | Gold: {state.gold}")
    return messages
