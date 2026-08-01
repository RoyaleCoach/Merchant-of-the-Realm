"""Inventory system — buy, sell, deposit, withdraw, warehouse management."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import get_item

log = get_logger(__name__)

# Default weight per unit for items not explicitly weighted
DEFAULT_WEIGHT = 1


def _item_weight(item_id: str) -> int:
    """Get the weight per unit of an item (currently default 1)."""
    return DEFAULT_WEIGHT


def _add_to_inventory(storage: list[dict], item_id: str, name: str, quantity: int, weight: int = DEFAULT_WEIGHT) -> None:
    """Add items to a storage list (inventory or warehouse). Stacks by item_id."""
    for entry in storage:
        if entry["item_id"] == item_id:
            entry["quantity"] += quantity
            return
    storage.append({
        "item_id": item_id,
        "name": name,
        "quantity": quantity,
        "weight": weight,
    })


def _remove_from_inventory(storage: list[dict], item_id: str, quantity: int) -> bool:
    """Remove items from a storage list. Returns False if not enough."""
    for i, entry in enumerate(storage):
        if entry["item_id"] == item_id:
            if entry["quantity"] < quantity:
                return False
            entry["quantity"] -= quantity
            if entry["quantity"] <= 0:
                storage.pop(i)
            return True
    return False


def buy(state: GameState, item_id: str, quantity: int) -> str:
    """
    Buy items from the market.
    Validates: item exists, market stock, player gold, inventory space.
    Returns a result message.
    """
    # Find item on market
    market_item = None
    for m in state.market:
        if m["item_id"] == item_id:
            market_item = m
            break

    if market_item is None:
        return f"Item '{item_id}' not found on the market."

    if quantity <= 0:
        return "Quantity must be positive."

    # Check market stock
    if market_item["supply"] < quantity:
        return f"Not enough {market_item['name']} in stock. Available: {market_item['supply']}."

    # Calculate cost
    cost = market_item["current_price"] * quantity
    if state.gold < cost:
        return f"Not enough gold. Need {cost}g, have {state.gold}g."

    # Check inventory capacity
    weight = _item_weight(item_id)
    total_weight = weight * quantity
    if state.inventory_free_space < total_weight:
        return f"Not enough inventory space. Need {total_weight}, free: {state.inventory_free_space}."

    # Execute transaction
    state.gold -= cost
    market_item["supply"] -= quantity
    _add_to_inventory(state.inventory, item_id, market_item["name"], quantity, weight)

    log.info(f"Bought {quantity}x {market_item['name']} for {cost}g")
    return f"Bought {quantity}x {market_item['name']} for {cost}g."


def sell(state: GameState, item_id: str, quantity: int) -> str:
    """
    Sell items to the market.
    Validates: item exists in inventory, quantity.
    Returns a result message.
    """
    # Find item in inventory
    inv_item = state.inventory_item(item_id)
    if inv_item is None:
        return f"You don't have any '{item_id}' in your inventory."

    if quantity <= 0:
        return "Quantity must be positive."

    if inv_item["quantity"] < quantity:
        return f"You only have {inv_item['quantity']}x {inv_item['name']}."

    # Find market price
    market_item = None
    for m in state.market:
        if m["item_id"] == item_id:
            market_item = m
            break

    if market_item is None:
        return f"No market for '{item_id}'."

    # Execute transaction (sell at 90% of market price)
    price = max(1, int(market_item["current_price"] * 0.9))
    revenue = price * quantity
    state.gold += revenue
    market_item["supply"] += quantity
    _remove_from_inventory(state.inventory, item_id, quantity)

    log.info(f"Sold {quantity}x {inv_item['name']} for {revenue}g")
    return f"Sold {quantity}x {inv_item['name']} for {revenue}g ({price}g each)."


def deposit(state: GameState, item_id: str, quantity: int) -> str:
    """
    Move items from inventory to warehouse.
    Validates: item in inventory, quantity, warehouse space.
    Returns a result message.
    """
    inv_item = state.inventory_item(item_id)
    if inv_item is None:
        return f"You don't have any '{item_id}' in your inventory."

    if quantity <= 0:
        return "Quantity must be positive."

    if inv_item["quantity"] < quantity:
        return f"You only have {inv_item['quantity']}x {inv_item['name']}."

    weight = inv_item.get("weight", DEFAULT_WEIGHT)
    total_weight = weight * quantity
    if state.warehouse_free_space < total_weight:
        return f"Not enough warehouse space. Need {total_weight}, free: {state.warehouse_free_space}."

    _remove_from_inventory(state.inventory, item_id, quantity)
    _add_to_inventory(state.warehouse, item_id, inv_item["name"], quantity, weight)

    log.info(f"Deposited {quantity}x {inv_item['name']} to warehouse")
    return f"Deposited {quantity}x {inv_item['name']} to warehouse."


def withdraw(state: GameState, item_id: str, quantity: int) -> str:
    """
    Move items from warehouse to inventory.
    Validates: item in warehouse, quantity, inventory space.
    Returns a result message.
    """
    wh_item = state.warehouse_item(item_id)
    if wh_item is None:
        return f"No '{item_id}' in warehouse."

    if quantity <= 0:
        return "Quantity must be positive."

    if wh_item["quantity"] < quantity:
        return f"Warehouse only has {wh_item['quantity']}x {wh_item['name']}."

    weight = wh_item.get("weight", DEFAULT_WEIGHT)
    total_weight = weight * quantity
    if state.inventory_free_space < total_weight:
        return f"Not enough inventory space. Need {total_weight}, free: {state.inventory_free_space}."

    _remove_from_inventory(state.warehouse, item_id, quantity)
    _add_to_inventory(state.inventory, item_id, wh_item["name"], quantity, weight)

    log.info(f"Withdrew {quantity}x {wh_item['name']} from warehouse")
    return f"Withdrew {quantity}x {wh_item['name']} from warehouse."
