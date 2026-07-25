"""World generation — procedural kingdom, town, market, NPCs, and buildings."""

import random
from dataclasses import dataclass

from src.core.config import DEFAULT_STARTING_GOLD
from src.core.logger import get_logger
from src.utils.data_loader import get_npc_traits, get_all_items, get_all_buildings

log = get_logger(__name__)


@dataclass
class MarketItem:
    """An item currently on the market."""
    item_id: str
    name: str
    category: str
    base_price: int
    current_price: int
    supply: int
    demand: int


@dataclass
class NPC:
    """A generated NPC."""
    name: str
    profession: str
    gold: int
    mood: str


@dataclass
class Building:
    """A building in the town."""
    building_id: str
    name: str
    level: int
    workers: int
    max_workers: int


@dataclass
class World:
    """A fully generated game world."""
    kingdom_name: str
    town_name: str
    population: int
    gold: int
    weather: str
    market: list[MarketItem]
    npcs: list[NPC]
    buildings: list[Building]


def _random_name(traits: dict) -> str:
    """Generate a random NPC name."""
    return random.choice(traits["first_names"])


def generate_world(
    player_name: str = "Merchant",
    town_name: str | None = None,
    kingdom_name: str | None = None,
) -> World:
    """Generate a complete game world."""
    traits = get_npc_traits()
    items = get_all_items()
    buildings = get_all_buildings()

    # Kingdom & Town
    kingdom = kingdom_name or random.choice(traits["kingdom_names"])
    town = town_name or random.choice(traits["town_names"])
    population = random.randint(300, 800)
    gold = DEFAULT_STARTING_GOLD
    weather = "Sunny"

    # Generate market from items data
    market = _generate_market(items)

    # Generate NPCs
    npcs = _generate_npcs(traits, count=random.randint(5, 10))

    # Generate starting buildings
    starting_buildings = _generate_starting_buildings(buildings)

    world = World(
        kingdom_name=kingdom,
        town_name=town,
        population=population,
        gold=gold,
        weather=weather,
        market=market,
        npcs=npcs,
        buildings=starting_buildings,
    )

    log.info(f"Generated world: {town}, {kingdom} (pop: {population})")
    return world


def _generate_market(items: dict) -> list[MarketItem]:
    """Create initial market with randomized supply/demand."""
    market = []
    for item_id, data in items.items():
        supply = random.randint(20, 80)
        demand = random.randint(20, 80)
        # Price fluctuates ±20% from base based on supply vs demand
        ratio = demand / max(supply, 1)
        fluctuation = 1.0 + (ratio - 1.0) * 0.4
        current = max(1, int(data["base_price"] * fluctuation))
        market.append(MarketItem(
            item_id=item_id,
            name=data["name"],
            base_price=data["base_price"],
            current_price=current,
            supply=supply,
            demand=demand,
        ))
    return market


def _generate_npcs(traits: dict, count: int) -> list[NPC]:
    """Generate random NPCs."""
    npcs = []
    for _ in range(count):
        npcs.append(NPC(
            name=_random_name(traits),
            profession=random.choice(traits["professions"]),
            gold=random.randint(10, 200),
            mood=random.choice(traits["moods"]),
        ))
    return npcs


def _generate_starting_buildings(all_buildings: dict) -> list[Building]:
    """Create a few starting buildings for the town."""
    # Start with 3 basic buildings
    starter_ids = ["farm", "bakery", "lumber_mill"]
    result = []
    for bid in starter_ids:
        if bid in all_buildings:
            b = all_buildings[bid]
            result.append(Building(
                building_id=bid,
                name=b["name"],
                level=1,
                workers=1,
                max_workers=b["max_workers"],
            ))
    return result
