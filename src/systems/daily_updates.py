"""Daily update systems — economy, production, NPCs, weather, events."""

import random

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data

log = get_logger(__name__)


def update_economy(state: GameState, weather_mod: float) -> list[str]:
    """
    Update market prices based on supply/demand and production.
    Returns messages about significant price changes.
    """
    messages = []

    for item in state.market:
        # Random supply/demand fluctuation (±5)
        item["supply"] = max(0, item["supply"] + random.randint(-5, 5))
        item["demand"] = max(0, item["demand"] + random.randint(-5, 5))

        # Production adds to supply
        production = int(item.get("production_rate", 30) * weather_mod)
        item["supply"] += production

        # Consumption reduces supply, increases demand pressure
        consumption = item.get("consumption_rate", 25)
        item["supply"] = max(0, item["supply"] - consumption)
        item["demand"] += consumption // 2

        # Recalculate price: ratio of demand to supply
        ratio = item["demand"] / max(item["supply"], 1)
        fluctuation = 1.0 + (ratio - 1.0) * 0.3
        new_price = max(1, min(item["base_price"] * 2, int(item["base_price"] * fluctuation)))

        # Report significant changes
        old_price = item["current_price"]
        if abs(new_price - old_price) >= 3:
            direction = "↑" if new_price > old_price else "↓"
            messages.append(f"  {item['name']}: {old_price}g → {new_price}g ({direction})")

        item["current_price"] = new_price

    return messages


def update_production(state: GameState, weather_mod: float) -> list[str]:
    """
    Process goods flow through supply chains.
    Producers create goods, consumers pull inputs.
    Returns messages about production and shortages.
    """
    from src.systems.supply_chain import process_goods_flow

    messages = []

    # Process the actual flow of goods
    flow_msgs = process_goods_flow(state, weather_mod)
    messages.extend(flow_msgs)

    # Add production output messages for active buildings
    buildings_data = load_data("buildings.json")
    for b in state.buildings:
        if b["workers"] <= 0:
            continue

        bdata = buildings_data.get(b["building_id"], {})
        produces = bdata.get("produces")
        if not produces:
            continue

        from src.systems.workforce import get_worker_modifier
        worker_mod = get_worker_modifier(state, b["building_id"])
        worker_ratio = b["workers"] / max(b["max_workers"], 1)
        output = int(10 * worker_ratio * weather_mod * b["level"] * worker_mod)

        if output > 0:
            # Find market item name
            item_name = produces.capitalize()
            for m in state.market:
                if m["item_id"] == produces:
                    item_name = m["name"]
                    break
            messages.append(f"  {b['name']} produced {output} {item_name}")

    return messages


def update_npcs(state: GameState, mood_shift: int) -> list[str]:
    """
    Update NPC behavior based on daily conditions.
    Delegates to npc_system for full behavior update.
    Returns messages about notable NPC changes.
    """
    from src.systems.npc_system import update_npc_behavior

    messages = []
    update_npc_behavior(state, mood_shift)

    return messages


def update_weather(state: GameState) -> str | None:
    """
    Possibly change weather based on season weights.
    Returns a message if weather changed, None otherwise.
    """
    weather_data = load_data("weather.json")
    season_weights = weather_data.get("season_weights", {}).get(state.season, {})

    if not season_weights:
        return None

    # 30% chance of weather change each day
    if random.random() > 0.3:
        return None

    # Weighted random selection
    pool = []
    for wname, weight in season_weights.items():
        pool.extend([wname] * weight)

    if not pool:
        return None

    new_weather = random.choice(pool)
    if new_weather != state.weather:
        old_weather = state.weather
        state.weather = new_weather
        # Find icon
        icon = ""
        for wt in weather_data.get("types", []):
            if wt["name"] == new_weather:
                icon = wt.get("icon", "")
                break
        return f"Weather changed: {old_weather} → {icon} {new_weather}"

    return None


def roll_events(state: GameState) -> list[str]:
    """
    Roll for daily random events.
    Returns list of event messages.
    """
    messages = []
    events_data = load_data("events.json")

    # Check for daily event
    daily_events = events_data.get("daily", [])
    roll = random.random()
    cumulative = 0.0
    for event in daily_events:
        cumulative += event["chance"]
        if roll <= cumulative:
            messages.append(event["text"])
            # Apply effects
            state.gold = max(0, state.gold + event["effect"].get("gold", 0))
            break

    return messages


def is_season_start(state: GameState) -> bool:
    """Check if today is the first day of a new season."""
    return state.day == 1 and state.week == 1 and state.month == 1


def roll_seasonal_events(state: GameState) -> list[str]:
    """Roll for seasonal events at the start of each season."""
    messages = []
    events_data = load_data("events.json")
    seasonal = events_data.get("seasonal", {}).get(state.season, [])

    if seasonal:
        event = random.choice(seasonal)
        messages.append(f"🌟 {event['text']}")
        state.gold = max(0, state.gold + event["effect"].get("gold", 0))

    return messages


def get_weather_mod(state: GameState) -> float:
    """Get the production modifier for current weather."""
    weather_data = load_data("weather.json")
    for wt in weather_data.get("types", []):
        if wt["name"] == state.weather:
            return wt.get("production_mod", 1.0)
    return 1.0


def get_mood_mod(state: GameState) -> int:
    """Get the mood modifier for current weather."""
    weather_data = load_data("weather.json")
    for wt in weather_data.get("types", []):
        if wt["name"] == state.weather:
            return wt.get("mood_mod", 0)
    return 0
