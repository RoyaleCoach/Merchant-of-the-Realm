"""Town expansion system — automatic tier progression based on population."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data

log = get_logger(__name__)


def get_tiers() -> list[dict]:
    """Get all tier definitions sorted by threshold."""
    data = load_data("town_tiers.json")
    return sorted(data.get("tiers", []), key=lambda t: t["threshold"])


def get_current_tier(state: GameState) -> dict:
    """Get the tier for a given population."""
    tiers = get_tiers()
    current = tiers[0]
    for tier in tiers:
        if state.population >= tier["threshold"]:
            current = tier
        else:
            break
    return current


def get_next_tier(state: GameState) -> dict | None:
    """Get the next tier above current, or None if at max."""
    tiers = get_tiers()
    for tier in tiers:
        if state.population < tier["threshold"]:
            return tier
    return None


def check_promotion(state: GameState) -> tuple[dict | None, str | None]:
    """
    Check if the town should be promoted to a new tier.
    Returns (new_tier, message) if promoted, (None, None) otherwise.
    """
    new_tier = get_current_tier(state)

    # Compare with stored tier
    if new_tier["id"] != state.town_tier:
        old_tier_name = state.town_tier
        state.town_tier = new_tier["id"]

        # Get promotion message
        data = load_data("town_tiers.json")
        msg = data.get("promotion_messages", {}).get(new_tier["id"])
        if msg is None:
            msg = f"⭐ Your town has been promoted to {new_tier['icon']} {new_tier['name']}!"

        log.info(f"Town promoted: {old_tier_name} → {new_tier['id']} (pop {state.population})")
        return new_tier, msg

    return None, None


def get_tier_progress(state: GameState) -> dict:
    """Get progress toward next tier."""
    current = get_current_tier(state)
    next_tier = get_next_tier(state)

    if next_tier is None:
        return {
            "current": current,
            "next": None,
            "progress": 100,
            "remaining": 0,
        }

    span = next_tier["threshold"] - current["threshold"]
    earned = state.population - current["threshold"]
    progress = min(100, int((earned / span) * 100)) if span > 0 else 100

    return {
        "current": current,
        "next": next_tier,
        "progress": progress,
        "remaining": next_tier["threshold"] - state.population,
    }


def get_max_buildings(state: GameState) -> int:
    """Get max buildings allowed at current tier."""
    tier = get_current_tier(state)
    return tier["max_buildings"]


def is_building_unlocked(state: GameState, building_id: str) -> bool:
    """Check if a building type is unlocked at the current tier."""
    tier = get_current_tier(state)
    unlocked = tier.get("unlocks", [])
    # If building is in the unlocks list for this tier or any lower tier
    for t in get_tiers():
        if t["threshold"] <= tier["threshold"]:
            if building_id in t.get("unlocks", []):
                return True
    return False


def get_demand_multiplier(state: GameState) -> float:
    """Get demand multiplier from town tier perks."""
    tier = get_current_tier(state)
    return tier["perks"]["demand_multiplier"]


def get_migration_bonus(state: GameState) -> int:
    """Get migration bonus from town tier."""
    tier = get_current_tier(state)
    return tier["perks"]["migration_bonus"]


def get_all_unlocked_buildings(state: GameState) -> list[str]:
    """Get all building IDs unlocked at current tier."""
    tier = get_current_tier(state)
    unlocked = []
    for t in get_tiers():
        if t["threshold"] <= tier["threshold"]:
            unlocked.extend(t.get("unlocks", []))
    return list(set(unlocked))
