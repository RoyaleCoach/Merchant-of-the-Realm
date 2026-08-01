"""Building system — construct, upgrade, demolish buildings."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import get_all_buildings, get_building

log = get_logger(__name__)

# Upgrade cost scales with level: base_cost * level * 1.5
UPGRADE_COST_MULTIPLIER = 1.5

# Demolish refund: 50% of original cost
DEMOLISH_REFUND_RATE = 0.5

# Max building level
MAX_LEVEL = 5


def get_building_data(building_id: str) -> dict | None:
    """Get building definition from buildings.json."""
    return get_building(building_id)


def get_constructible_buildings(state: GameState) -> list[dict]:
    """Get all buildings that can be constructed (not already built, or below max level)."""
    all_buildings = get_all_buildings()
    owned_ids = {b["building_id"] for b in state.buildings}
    result = []
    for bid, bdata in all_buildings.items():
        if bid not in owned_ids:
            result.append({"building_id": bid, **bdata})
    return result


def get_upgrade_cost(building_id: str, current_level: int) -> int:
    """Calculate upgrade cost based on building base cost and current level."""
    bdata = get_building_data(building_id)
    if bdata is None:
        return 0
    return int(bdata["cost"] * current_level * UPGRADE_COST_MULTIPLIER)


def get_demolish_refund(building_id: str) -> int:
    """Calculate refund for demolishing a building."""
    bdata = get_building_data(building_id)
    if bdata is None:
        return 0
    return int(bdata["cost"] * DEMOLISH_REFUND_RATE)


def build(state: GameState, building_id: str) -> str:
    """
    Construct a new building.
    Validates: building exists, not enough gold, not already built.
    Returns a result message.
    """
    bdata = get_building_data(building_id)
    if bdata is None:
        return f"Unknown building type '{building_id}'."

    # Check if already built
    for b in state.buildings:
        if b["building_id"] == building_id:
            return f"{bdata['name']} already exists in town. Use 'upgrade' to improve it."

    cost = bdata["cost"]
    if state.gold < cost:
        return f"Not enough gold. Need {cost}g, have {state.gold}g."

    # Execute construction
    state.gold -= cost
    state.buildings.append({
        "building_id": building_id,
        "name": bdata["name"],
        "level": 1,
        "workers": 0,
        "max_workers": bdata["max_workers"],
    })

    log.info(f"Built {bdata['name']} for {cost}g")
    return f"Constructed {bdata['name']} for {cost}g. Hire workers to start production."


def upgrade(state: GameState, building_id: str) -> str:
    """
    Upgrade a building to the next level.
    Increases max workers and output.
    Returns a result message.
    """
    for b in state.buildings:
        if b["building_id"] == building_id:
            if b["level"] >= MAX_LEVEL:
                return f"{b['name']} is already at max level ({MAX_LEVEL})."

            cost = get_upgrade_cost(building_id, b["level"])
            if state.gold < cost:
                return f"Not enough gold. Need {cost}g, have {state.gold}g."

            # Execute upgrade
            state.gold -= cost
            b["level"] += 1
            bdata = get_building_data(building_id)
            if bdata:
                # Increase max workers by the building's base max_workers
                b["max_workers"] = bdata["max_workers"] * b["level"]

            log.info(f"Upgraded {b['name']} to level {b['level']} for {cost}g")
            return f"Upgraded {b['name']} to level {b['level']} for {cost}g. Max workers: {b['max_workers']}."

    return f"No building '{building_id}' found in town."


def demolish(state: GameState, building_id: str) -> str:
    """
    Demolish a building for partial refund.
    Returns a result message.
    """
    for i, b in enumerate(state.buildings):
        if b["building_id"] == building_id:
            refund = get_demolish_refund(building_id)
            name = b["name"]
            state.gold += refund
            state.buildings.pop(i)

            log.info(f"Demolished {name}, refunded {refund}g")
            return f"Demolished {name}. Refunded {refund}g."

    return f"No building '{building_id}' found in town."


def get_building_efficiency(building: dict) -> float:
    """Calculate building efficiency based on worker ratio."""
    if building["max_workers"] <= 0:
        return 0.0
    return building["workers"] / building["max_workers"]


def get_building_output(building: dict, weather_mod: float = 1.0) -> int:
    """Calculate daily output for a building."""
    bdata = get_building_data(building["building_id"])
    if bdata is None or building["workers"] <= 0:
        return 0

    efficiency = get_building_efficiency(building)
    base_output = 10 * building["level"]
    return int(base_output * efficiency * weather_mod)


def get_building_info(building: dict) -> dict:
    """Get detailed info about a building for display."""
    bdata = get_building_data(building["building_id"])
    if bdata is None:
        return {}

    efficiency = get_building_efficiency(building)
    upgrade_cost = get_upgrade_cost(building["building_id"], building["level"])
    demolish_refund = get_demolish_refund(building["building_id"])

    return {
        "building_id": building["building_id"],
        "name": building["name"],
        "level": building["level"],
        "workers": building["workers"],
        "max_workers": building["max_workers"],
        "efficiency": efficiency,
        "maintenance": bdata["maintenance"],
        "produces": bdata.get("produces"),
        "requires": bdata.get("requires"),
        "description": bdata.get("description", ""),
        "upgrade_cost": upgrade_cost if building["level"] < MAX_LEVEL else 0,
        "demolish_refund": demolish_refund,
        "max_level": MAX_LEVEL,
    }
