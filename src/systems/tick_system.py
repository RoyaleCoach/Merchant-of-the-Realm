"""Tick system — advances time and triggers all daily updates."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.systems.daily_updates import (
    update_economy,
    update_production,
    update_npcs,
    update_weather,
    is_season_start,
    roll_seasonal_events,
    get_weather_mod,
    get_mood_mod,
)
from src.systems.season_effects import roll_season_event
from src.systems.event_engine import roll_daily_event, roll_major_event
from src.systems.reputation import daily_reputation_tick
from src.systems.town_expansion import check_promotion, get_migration_bonus
from src.systems.multi_town import update_foreign_markets
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
    daily_msg, _ = roll_daily_event(state)
    if daily_msg:
        messages.append(daily_msg)

    # Major events (5% chance, player choices)
    major_msg, choices = roll_major_event(state)
    if major_msg:
        messages.append(major_msg)
        if choices:
            # Store choices for the game loop to handle
            state.pending_choices = choices
            state.pending_event_text = major_msg
        else:
            state.pending_choices = []
    else:
        state.pending_choices = []

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

    # Daily reputation changes (crime penalty, etc.)
    rep_change = daily_reputation_tick(state)
    if rep_change != 0:
        messages.append(f"  Reputation: {rep_change:+d} (high crime hurts your standing)")

    # Update neighboring town markets
    if state.neighboring_towns:
        update_foreign_markets(state)

    # Town expansion check
    new_tier, promo_msg = check_promotion(state)
    if new_tier and promo_msg:
        messages.append(f"  {promo_msg}")

    log.info(f"Tick: {state.date_string} | Weather: {state.weather} | Gold: {state.gold} | Rep: {state.reputation}")
    return messages
