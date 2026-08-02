"""Multi-town economy — neighboring towns with unique prices and arbitrage."""

import random

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data, get_all_items

log = get_logger(__name__)


def get_town_definitions() -> list[dict]:
    """Get all neighboring town definitions."""
    data = load_data("towns.json")
    return data.get("towns", [])


def get_town_definition(town_id: str) -> dict | None:
    """Get a specific town definition by ID."""
    for town in get_town_definitions():
        if town["id"] == town_id:
            return town
    return None


def generate_town_market(town_def: dict) -> list[dict]:
    """
    Generate a market for a neighboring town.
    Each town has unique prices based on abundant/scarce resources.
    """
    items = get_all_items()
    market = []

    for item_id, data in items.items():
        base_price = data["base_price"]
        modifiers = town_def.get("price_modifiers", {})
        mod = modifiers.get(item_id, 1.0)

        # Abundant items have high supply, scarce have low
        if item_id in town_def.get("abundant", []):
            supply = random.randint(60, 120)
            demand = random.randint(10, 40)
        elif item_id in town_def.get("scarce", []):
            supply = random.randint(5, 25)
            demand = random.randint(50, 90)
        else:
            supply = random.randint(20, 60)
            demand = random.randint(20, 60)

        # Apply town price modifier
        current_price = max(1, int(base_price * mod))

        market.append({
            "item_id": item_id,
            "name": data["name"],
            "category": data.get("category", "general"),
            "base_price": base_price,
            "current_price": current_price,
            "supply": supply,
            "demand": demand,
        })

    return market


def init_neighboring_towns(state: GameState) -> None:
    """Generate all neighboring towns and store in game state."""
    towns = []
    for town_def in get_town_definitions():
        market = generate_town_market(town_def)
        towns.append({
            "id": town_def["id"],
            "name": town_def["name"],
            "description": town_def["description"],
            "population": town_def["population"],
            "specialty": town_def["specialty"],
            "abundant": town_def.get("abundant", []),
            "scarce": town_def.get("scarce", []),
            "price_modifiers": town_def.get("price_modifiers", {}),
            "demand_focus": town_def.get("demand_focus", []),
            "icon": town_def.get("icon", "🏘️"),
            "market": market,
            "visited": False,
        })

    state.neighboring_towns = towns
    log.info(f"Generated {len(towns)} neighboring towns")


def get_town_by_id(state: GameState, town_id: str) -> dict | None:
    """Get a neighboring town by ID."""
    for town in state.neighboring_towns:
        if town["id"] == town_id:
            return town
    return None


def get_town_market(state: GameState, town_id: str) -> list[dict] | None:
    """Get the market for a specific town."""
    town = get_town_by_id(state, town_id)
    if town:
        return town["market"]
    return None


def get_arbitrage_opportunities(state: GameState, town_id: str) -> list[dict]:
    """
    Find profitable trade routes between home town and a neighboring town.
    Returns items where price difference > 20%.
    """
    town = get_town_by_id(state, town_id)
    if not town:
        return []

    opportunities = []
    home_market = {m["item_id"]: m for m in state.market}

    for foreign_item in town["market"]:
        item_id = foreign_item["item_id"]
        home_item = home_market.get(item_id)
        if not home_item:
            continue

        home_price = home_item["current_price"]
        foreign_price = foreign_item["current_price"]

        # Buy cheap here, sell there (or vice versa)
        if home_price > 0:
            margin = (foreign_price - home_price) / home_price
            if abs(margin) >= 0.15:
                if margin > 0:
                    # Buy at home, sell abroad
                    opportunities.append({
                        "item_id": item_id,
                        "name": foreign_item["name"],
                        "buy_price": home_price,
                        "sell_price": foreign_price,
                        "margin_pct": int(margin * 100),
                        "direction": "export",
                        "foreign_town": town["name"],
                    })
                else:
                    # Buy abroad, sell at home
                    opportunities.append({
                        "item_id": item_id,
                        "name": foreign_item["name"],
                        "buy_price": foreign_price,
                        "sell_price": home_price,
                        "margin_pct": int(abs(margin) * 100),
                        "direction": "import",
                        "foreign_town": town["name"],
                    })

    # Sort by margin
    opportunities.sort(key=lambda x: x["margin_pct"], reverse=True)
    return opportunities


def travel_to_town(state: GameState, town_id: str) -> dict | None:
    """
    Travel to a neighboring town. Advances 1 day.
    Returns town info or None if not found.
    """
    town = get_town_by_id(state, town_id)
    if not town:
        return None

    town["visited"] = True
    state.current_town = town_id
    log.info(f"Traveled to {town['name']}")
    return town


def return_home(state: GameState) -> None:
    """Return to home town."""
    state.current_town = ""


def is_abroad(state: GameState) -> bool:
    """Check if player is currently in a neighboring town."""
    return state.current_town != ""


def get_current_town_market(state: GameState) -> list[dict]:
    """Get market for current location (home or abroad)."""
    if is_abroad(state):
        return get_town_market(state, state.current_town) or []
    return state.market


def get_current_town_info(state: GameState) -> dict | None:
    """Get info for current town."""
    if is_abroad(state):
        return get_town_by_id(state, state.current_town)
    return None


def update_foreign_markets(state: GameState) -> None:
    """Update prices in neighboring towns (called daily)."""
    for town in state.neighboring_towns:
        for item in town["market"]:
            # Small random fluctuation
            item["supply"] = max(0, item["supply"] + random.randint(-3, 3))
            item["demand"] = max(0, item["demand"] + random.randint(-3, 3))

            # Recalculate price based on supply/demand
            ratio = item["demand"] / max(item["supply"], 1)
            base_mod = town["price_modifiers"].get(item["item_id"], 1.0)
            fluctuation = 1.0 + (ratio - 1.0) * 0.2
            item["current_price"] = max(1, int(item["base_price"] * base_mod * fluctuation))
