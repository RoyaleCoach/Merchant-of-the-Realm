"""NPC system — merchant generation, attributes, recruitment, behavior."""

import random

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import get_npc_traits

log = get_logger(__name__)


def get_npc(state: GameState, name: str) -> dict | None:
    """Find an NPC by name (case-insensitive partial match)."""
    name_lower = name.lower()
    for npc in state.npcs:
        if name_lower in npc["name"].lower():
            return npc
    return None


def get_npc_info(npc: dict) -> dict:
    """Get detailed info about an NPC for display."""
    loyalty = npc.get("loyalty", 50)
    greed = npc.get("greed", 50)
    reputation = npc.get("reputation", 50)
    relationship = npc.get("relationship", 50)

    # Derive labels
    if loyalty >= 70:
        loyalty_label = "Loyal"
    elif loyalty >= 40:
        loyalty_label = "Neutral"
    else:
        loyalty_label = "Disloyal"

    if greed >= 70:
        greed_label = "Greedy"
    elif greed >= 40:
        greed_label = "Fair"
    else:
        greed_label = "Generous"

    if reputation >= 70:
        rep_label = "Respected"
    elif reputation >= 40:
        rep_label = "Known"
    else:
        rep_label = "Disliked"

    if relationship >= 70:
        rel_label = "Friend"
    elif relationship >= 40:
        rel_label = "Acquaintance"
    else:
        rel_label = "Stranger"

    mood = npc.get("mood", "Neutral")
    mood_icon = {"Happy": "😊", "Content": "🙂", "Neutral": "😐", "Worried": "😟", "Angry": "😠"}.get(mood, "•")

    return {
        "name": npc["name"],
        "age": npc.get("age", 25),
        "profession": npc["profession"],
        "gold": npc["gold"],
        "mood": mood,
        "mood_icon": mood_icon,
        "loyalty": loyalty,
        "loyalty_label": loyalty_label,
        "greed": greed,
        "greed_label": greed_label,
        "reputation": reputation,
        "rep_label": rep_label,
        "relationship": relationship,
        "rel_label": rel_label,
        "workplace": npc.get("workplace"),
        "inventory": npc.get("inventory", []),
    }


def recruit(state: GameState, npc_name: str, building_id: str) -> str:
    """
    Assign an NPC to work at a building.
    Validates: NPC exists, building exists, NPC not already employed elsewhere.
    Returns a result message.
    """
    npc = get_npc(state, npc_name)
    if npc is None:
        return f"No NPC matching '{npc_name}' found."

    # Find the building
    building = None
    for b in state.buildings:
        if b["building_id"] == building_id:
            building = b
            break

    if building is None:
        return f"No building '{building_id}' found."

    # Check if building is full
    if building["workers"] >= building["max_workers"]:
        return f"{building['name']} is at max capacity ({building['max_workers']} workers)."

    # Check if NPC already works here
    if npc.get("workplace") == building_id:
        return f"{npc['name']} already works at {building['name']}."

    # Remove NPC from previous workplace
    prev_building = npc.get("workplace")
    if prev_building:
        for b in state.buildings:
            if b["building_id"] == prev_building:
                b["workers"] = max(0, b["workers"] - 1)
                break

    # Assign NPC to new workplace
    npc["workplace"] = building_id
    building["workers"] += 1

    # Improve relationship
    npc["relationship"] = min(100, npc.get("relationship", 50) + 5)

    log.info(f"Recruited {npc['name']} to {building['name']}")
    return f"{npc['name']} now works at {building['name']}. (Relationship +5)"


def dismiss(state: GameState, npc_name: str) -> str:
    """Remove an NPC from their workplace."""
    npc = get_npc(state, npc_name)
    if npc is None:
        return f"No NPC matching '{npc_name}' found."

    workplace = npc.get("workplace")
    if workplace is None:
        return f"{npc['name']} is not employed."

    for b in state.buildings:
        if b["building_id"] == workplace:
            b["workers"] = max(0, b["workers"] - 1)
            bname = b["name"]
            break

    npc["workplace"] = None
    npc["relationship"] = max(0, npc.get("relationship", 50) - 10)

    log.info(f"Dismissed {npc['name']} from {bname}")
    return f"{npc['name']} dismissed from {bname}. (Relationship -10)"


def get_available_npcs(state: GameState) -> list[dict]:
    """Get NPCs who are not currently employed."""
    return [n for n in state.npcs if n.get("workplace") is None]


def get_employed_npcs(state: GameState) -> list[dict]:
    """Get NPCs who are currently employed."""
    return [n for n in state.npcs if n.get("workplace") is not None]


def update_npc_behavior(state: GameState, mood_shift: int) -> None:
    """
    Daily NPC behavior update.
    Updates mood, gold, loyalty drift, reputation, relationship.
    """
    moods = ["Angry", "Worried", "Neutral", "Content", "Happy"]

    for npc in state.npcs:
        # Mood drifts based on weather/events
        current_idx = moods.index(npc["mood"]) if npc["mood"] in moods else 2
        new_idx = max(0, min(len(moods) - 1, current_idx + mood_shift + random.randint(-1, 1)))
        npc["mood"] = moods[new_idx]

        # NPCs earn/spend gold based on employment
        if npc.get("workplace"):
            # Employed NPCs earn wages
            npc["gold"] += random.randint(5, 20)
            # Loyalty slowly increases when employed
            npc["loyalty"] = min(100, npc.get("loyalty", 50) + random.randint(0, 2))
        else:
            # Unemployed NPCs struggle
            npc["gold"] = max(0, npc["gold"] + random.randint(-5, 5))
            # Loyalty slowly decreases when unemployed
            npc["loyalty"] = max(0, npc.get("loyalty", 50) - random.randint(0, 1))

        # Reputation drifts slightly based on mood
        if npc["mood"] in ("Happy", "Content"):
            npc["reputation"] = min(100, npc.get("reputation", 50) + random.randint(0, 1))
        elif npc["mood"] in ("Angry", "Worried"):
            npc["reputation"] = max(0, npc.get("reputation", 50) - random.randint(0, 1))

        # Greed slowly increases over time (inflation pressure)
        if random.random() < 0.1:
            npc["greed"] = min(100, npc.get("greed", 50) + 1)
