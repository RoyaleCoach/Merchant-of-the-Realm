"""Citizens simulation — needs, happiness, crime, migration."""

import random

from src.core.game_state import GameState
from src.core.logger import get_logger

log = get_logger(__name__)

# Item categories mapped to citizen needs
FOOD_ITEMS = {"bread", "wheat", "salt", "fish", "meat", "ale"}
CLOTHING_ITEMS = {"cloth", "leather"}
TOOLS_ITEMS = {"tools"}
HOUSING_ITEMS = {"wood"}
LUXURY_ITEMS = {"wine"}

# Consumption rate per citizen per day (units)
BASE_CONSUMPTION_PER_CITIZEN = 0.05


def calculate_need_fulfillment(state: GameState, item_set: set[str]) -> int:
    """
    Calculate how well a specific need is met (0-100).
    Based on market supply relative to population demand.
    """
    total_supply = 0
    for item in state.market:
        if item["item_id"] in item_set:
            total_supply += item["supply"]

    # Demand: each citizen consumes BASE_CONSUMPTION per day
    demand = state.population * BASE_CONSUMPTION_PER_CITIZEN

    if demand <= 0:
        return 100

    ratio = total_supply / demand
    # ratio 0 = 0%, ratio 1 = 70%, ratio 2+ = 100%
    fulfillment = min(100, int(ratio * 70))
    return fulfillment


def update_needs(state: GameState) -> None:
    """Update all need fulfillment levels based on market supply."""
    state.food_supply = calculate_need_fulfillment(state, FOOD_ITEMS)
    state.clothing_supply = calculate_need_fulfillment(state, CLOTHING_ITEMS)
    state.tools_supply = calculate_need_fulfillment(state, TOOLS_ITEMS)
    state.housing_supply = calculate_need_fulfillment(state, HOUSING_ITEMS)
    state.luxury_supply = calculate_need_fulfillment(state, LUXURY_ITEMS)


def consume_goods(state: GameState) -> list[str]:
    """
    Citizens consume goods from the market daily.
    Returns messages about shortages.
    """
    messages = []
    pop = state.population

    # Calculate consumption for each need category
    consumption = {
        "food": int(pop * BASE_CONSUMPTION_PER_CITIZEN * 1.0),  # food is primary
        "clothing": int(pop * BASE_CONSUMPTION_PER_CITIZEN * 0.3),
        "tools": int(pop * BASE_CONSUMPTION_PER_CITIZEN * 0.2),
        "housing": int(pop * BASE_CONSUMPTION_PER_CITIZEN * 0.1),
        "luxury": int(pop * BASE_CONSUMPTION_PER_CITIZEN * 0.1),
    }

    # Consume food
    food_needed = consumption["food"]
    food_consumed = _consume_from_market(state, FOOD_ITEMS, food_needed)
    if food_consumed < food_needed * 0.5:
        messages.append(f"  [red]⚠ Food shortage! Citizens needed {food_needed}, only got {food_consumed}![/red]")

    # Consume clothing
    cloth_needed = consumption["clothing"]
    _consume_from_market(state, CLOTHING_ITEMS, cloth_needed)

    # Consume tools
    tools_needed = consumption["tools"]
    _consume_from_market(state, TOOLS_ITEMS, tools_needed)

    # Consume housing materials
    housing_needed = consumption["housing"]
    _consume_from_market(state, HOUSING_ITEMS, housing_needed)

    # Consume luxury
    luxury_needed = consumption["luxury"]
    _consume_from_market(state, LUXURY_ITEMS, luxury_needed)

    return messages


def _consume_from_market(state: GameState, item_set: set[str], amount: int) -> int:
    """Consume goods from market. Returns actual amount consumed."""
    consumed = 0
    for item in state.market:
        if item["item_id"] in item_set and consumed < amount:
            take = min(amount - consumed, item["supply"])
            item["supply"] = max(0, item["supply"] - take)
            consumed += take
    return consumed


def update_happiness(state: GameState) -> None:
    """
    Update population happiness based on need fulfillment.
    Food is most important (40%), then clothing (20%), tools (15%), housing (15%), luxury (10%).
    """
    food_weight = 0.40
    clothing_weight = 0.20
    tools_weight = 0.15
    housing_weight = 0.15
    luxury_weight = 0.10

    target = int(
        state.food_supply * food_weight +
        state.clothing_supply * clothing_weight +
        state.tools_supply * tools_weight +
        state.housing_supply * housing_weight +
        state.luxury_supply * luxury_weight
    )

    # Happiness drifts toward target
    if state.happiness < target:
        state.happiness = min(100, state.happiness + random.randint(1, 3))
    elif state.happiness > target:
        state.happiness = max(0, state.happiness - random.randint(1, 3))


def update_crime(state: GameState) -> None:
    """
    Crime increases when needs are unmet and happiness is low.
    Food shortages are the biggest driver.
    """
    # Base crime from unhappiness
    if state.happiness < 30:
        crime_increase = random.randint(2, 5)
    elif state.happiness < 50:
        crime_increase = random.randint(1, 3)
    elif state.happiness < 70:
        crime_increase = random.randint(0, 1)
    else:
        crime_increase = 0

    # Food shortage bonus crime
    if state.food_supply < 30:
        crime_increase += random.randint(1, 3)

    # Crime decreases when happiness is high
    if state.happiness > 70:
        crime_decrease = random.randint(1, 2)
    else:
        crime_decrease = 0

    state.crime = max(0, min(100, state.crime + crime_increase - crime_decrease))


def update_migration(state: GameState) -> int:
    """
    Calculate population change from migration.
    Positive happiness → people move in.
    Low happiness + high crime → people leave.
    Returns the population change.
    """
    if state.happiness >= 70:
        # Prosperous town attracts people
        migration = random.randint(1, 5)
    elif state.happiness >= 50:
        # Stable — slight growth
        migration = random.randint(0, 2)
    elif state.happiness >= 30:
        # Declining — people start leaving
        migration = random.randint(-3, 0)
    else:
        # Crisis — mass exodus
        migration = random.randint(-10, -3)

    # Town tier bonus
    from src.systems.town_expansion import get_migration_bonus
    migration += get_migration_bonus(state)

    # Crime penalty
    if state.crime > 70:
        migration -= random.randint(2, 5)
    elif state.crime > 50:
        migration -= random.randint(1, 3)

    # Apply migration
    old_pop = state.population
    state.population = max(10, state.population + migration)
    state.migration = migration

    actual_change = state.population - old_pop
    return actual_change


def process_daily_citizens(state: GameState) -> list[str]:
    """
    Full daily citizen simulation.
    Returns messages about notable events.
    """
    messages = []

    # 1. Citizens consume goods
    shortage_msgs = consume_goods(state)
    messages.extend(shortage_msgs)

    # 2. Recalculate needs
    update_needs(state)

    # 3. Update happiness
    update_happiness(state)

    # 4. Update crime
    update_crime(state)

    # 5. Update migration
    pop_change = update_migration(state)
    if pop_change > 0:
        messages.append(f"  [green]📈 +{pop_change} new citizens arrived[/green]")
    elif pop_change < 0:
        messages.append(f"  [red]📉 {abs(pop_change)} citizens left town[/red]")

    log.info(
        f"Citizens: pop={state.population}, happiness={state.happiness}, "
        f"crime={state.crime}, food={state.food_supply}"
    )
    return messages


def get_citizen_status(state: GameState) -> dict:
    """Get full citizen status for display."""
    needs = [
        ("Food", state.food_supply, "🍞"),
        ("Clothing", state.clothing_supply, "👕"),
        ("Tools", state.tools_supply, "🔧"),
        ("Housing", state.housing_supply, "🏠"),
        ("Luxury", state.luxury_supply, "🍷"),
    ]

    # Determine happiness label
    if state.happiness >= 70:
        happiness_label = "Happy"
        happiness_color = "green"
    elif state.happiness >= 50:
        happiness_label = "Content"
        happiness_color = "dim"
    elif state.happiness >= 30:
        happiness_label = "Unhappy"
        happiness_color = "yellow"
    else:
        happiness_label = "Miserable"
        happiness_color = "red"

    # Determine crime label
    if state.crime >= 70:
        crime_label = "Dangerous"
        crime_color = "red"
    elif state.crime >= 40:
        crime_label = "Moderate"
        crime_color = "yellow"
    elif state.crime >= 20:
        crime_label = "Low"
        crime_color = "dim"
    else:
        crime_label = "Peaceful"
        crime_color = "green"

    # Migration trend
    if state.migration > 0:
        migration_label = f"Growing (+{state.migration})"
        migration_color = "green"
    elif state.migration < 0:
        migration_label = f"Declining ({state.migration})"
        migration_color = "red"
    else:
        migration_label = "Stable"
        migration_color = "dim"

    return {
        "population": state.population,
        "happiness": state.happiness,
        "happiness_label": happiness_label,
        "happiness_color": happiness_color,
        "crime": state.crime,
        "crime_label": crime_label,
        "crime_color": crime_color,
        "migration": state.migration,
        "migration_label": migration_label,
        "migration_color": migration_color,
        "needs": needs,
        "avg_fulfillment": state.avg_need_fulfillment,
    }
