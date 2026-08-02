"""Reputation system — track player rank and unlock perks."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data

log = get_logger(__name__)


def get_ranks() -> list[dict]:
    """Get all rank definitions sorted by threshold."""
    data = load_data("reputation.json")
    return sorted(data.get("ranks", []), key=lambda r: r["threshold"])


def get_current_rank(rep: int) -> dict:
    """Get the rank for a given reputation value."""
    ranks = get_ranks()
    current = ranks[0]
    for rank in ranks:
        if rep >= rank["threshold"]:
            current = rank
        else:
            break
    return current


def get_next_rank(rep: int) -> dict | None:
    """Get the next rank above current, or None if at max."""
    ranks = get_ranks()
    for rank in ranks:
        if rep < rank["threshold"]:
            return rank
    return None


def get_rank_progress(rep: int) -> dict:
    """Get progress toward next rank."""
    current = get_current_rank(rep)
    next_rank = get_next_rank(rep)

    if next_rank is None:
        return {
            "current": current,
            "next": None,
            "progress": 100,
            "remaining": 0,
        }

    span = next_rank["threshold"] - current["threshold"]
    earned = rep - current["threshold"]
    progress = min(100, int((earned / span) * 100)) if span > 0 else 100

    return {
        "current": current,
        "next": next_rank,
        "progress": progress,
        "remaining": next_rank["threshold"] - rep,
    }


def add_reputation(state: GameState, amount: int, reason: str = "") -> tuple[int, dict | None]:
    """
    Add (or subtract) reputation. Returns (new_total, new_rank_or_none).
    If the rank changed, returns the new rank dict.
    """
    old_rank = get_current_rank(state.reputation)
    state.reputation = max(0, state.reputation + amount)
    new_rank = get_current_rank(state.reputation)

    if amount != 0:
        log.info(f"Reputation {amount:+d} ({reason}) → {state.reputation}")

    if new_rank["id"] != old_rank["id"]:
        return state.reputation, new_rank
    return state.reputation, None


def get_buy_discount(state: GameState) -> float:
    """Get buy price discount as a multiplier (0.0-1.0 off)."""
    rank = get_current_rank(state.reputation)
    return rank["perks"]["buy_discount"] / 100.0


def get_sell_bonus(state: GameState) -> float:
    """Get sell price bonus as a multiplier (0.0-1.0 extra)."""
    rank = get_current_rank(state.reputation)
    return rank["perks"]["sell_bonus"] / 100.0


def get_npc_quality_bonus(state: GameState) -> int:
    """Get bonus to NPC quality based on reputation."""
    rank = get_current_rank(state.reputation)
    return rank["perks"]["npc_quality"]


def get_effective_buy_price(state: GameState, base_price: int) -> int:
    """Calculate buy price after reputation discount."""
    discount = get_buy_discount(state)
    return max(1, int(base_price * (1 - discount)))


def get_effective_sell_price(state: GameState, base_price: int) -> int:
    """Calculate sell price after reputation bonus."""
    bonus = get_sell_bonus(state)
    return max(1, int(base_price * (1 + bonus)))


def is_royal_contract_unlocked(state: GameState) -> bool:
    """Check if royal contracts are available (Guild Master+)."""
    rank = get_current_rank(state.reputation)
    return rank["threshold"] >= 150


def is_exclusive_items_unlocked(state: GameState) -> bool:
    """Check if exclusive items are available (Royal Supplier+)."""
    rank = get_current_rank(state.reputation)
    return rank["threshold"] >= 300


def daily_reputation_tick(state: GameState) -> int:
    """
    Apply daily reputation changes (crime penalty, etc.).
    Returns net change.
    """
    change = 0

    # Crime penalty: high crime hurts reputation
    if state.crime > 50:
        penalty = -2
        change += penalty
        state.reputation = max(0, state.reputation + penalty)

    return change
