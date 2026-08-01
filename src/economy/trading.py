"""Trading system — market inspection, price analysis, trading workflow."""

from src.core.game_state import GameState
from src.core.logger import get_logger

log = get_logger(__name__)


def inspect_item(state: GameState, item_id: str) -> dict | None:
    """
    Get detailed info about a market item.
    Returns a dict with inspection data, or None if not found.
    """
    for m in state.market:
        if m["item_id"] == item_id:
            base = m["base_price"]
            current = m["current_price"]
            diff = current - base
            pct = ((current - base) / base) * 100 if base > 0 else 0
            supply = m["supply"]
            demand = m["demand"]
            ratio = demand / max(supply, 1)

            return {
                "item_id": m["item_id"],
                "name": m["name"],
                "category": m.get("category", "general"),
                "base_price": base,
                "current_price": current,
                "diff": diff,
                "pct": pct,
                "supply": supply,
                "demand": demand,
                "ratio": ratio,
            }
    return None


def get_affordability(state: GameState, item_id: str) -> dict | None:
    """Calculate how many of an item the player can afford."""
    for m in state.market:
        if m["item_id"] == item_id:
            price = m["current_price"]
            max_by_gold = state.gold // price if price > 0 else 0
            max_by_space = state.inventory_free_space  # weight=1 per item
            max_affordable = min(max_by_gold, max_by_space)
            return {
                "name": m["name"],
                "price": price,
                "max_by_gold": max_by_gold,
                "max_by_space": max_by_space,
                "max_affordable": max_affordable,
                "in_stock": m["supply"],
            }
    return None


def get_profitability(state: GameState, item_id: str) -> dict | None:
    """Calculate profit from selling items the player owns."""
    inv_item = state.inventory_item(item_id)
    if inv_item is None:
        return None

    for m in state.market:
        if m["item_id"] == item_id:
            sell_price = max(1, int(m["current_price"] * 0.9))
            return {
                "name": inv_item["name"],
                "quantity_owned": inv_item["quantity"],
                "market_price": m["current_price"],
                "sell_price": sell_price,
                "total_revenue": sell_price * inv_item["quantity"],
            }
    return None


def get_market_summary(state: GameState) -> list[dict]:
    """Get a summary of all market items with price trends."""
    summary = []
    for m in state.market:
        base = m["base_price"]
        current = m["current_price"]
        pct = ((current - base) / base) * 100 if base > 0 else 0
        summary.append({
            "item_id": m["item_id"],
            "name": m["name"],
            "category": m.get("category", "general"),
            "current_price": current,
            "base_price": base,
            "pct": pct,
            "supply": m["supply"],
            "demand": m["demand"],
        })
    return summary
