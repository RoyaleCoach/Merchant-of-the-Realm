"""Central game state — the single source of truth for all game data."""

from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class GameState:
    """Holds all data for a single playthrough."""

    # Identity
    name: str = "Save Slot"
    created_at: str = ""

    # World
    kingdom_name: str = ""
    town_name: str = ""
    population: int = 0
    weather: str = "Sunny"

    # Time
    day: int = 1        # 1-7 (day of week)
    week: int = 1       # 1-4 (week of month)
    month: int = 1      # 1-3 (month of season)
    season: str = "Spring"  # Spring, Summer, Autumn, Winter
    year: int = 1

    # Economy
    gold: int = 0
    reputation: int = 0  # 0+, player standing in the realm

    # Player
    player_name: str = ""

    # Inventory — items the player carries
    inventory: list[dict] = field(default_factory=list)
    inventory_capacity: int = 100  # max weight units

    # Warehouse — items stored in town warehouse
    warehouse: list[dict] = field(default_factory=list)
    warehouse_capacity: int = 500  # max weight units

    # Citizen simulation
    happiness: int = 50        # 0-100, overall population happiness
    crime: int = 10           # 0-100, crime level
    migration: int = 0        # net migration (positive = inflow)
    # Need fulfillment (0-100, how well each need is met)
    food_supply: int = 50
    clothing_supply: int = 50
    tools_supply: int = 50
    housing_supply: int = 50
    luxury_supply: int = 50

    # World entities (stored as dicts for JSON serialization)
    market: list[dict] = field(default_factory=list)
    npcs: list[dict] = field(default_factory=list)
    buildings: list[dict] = field(default_factory=list)

    # Event choices awaiting player decision
    pending_choices: list[dict] = field(default_factory=list)
    pending_event_text: str = ""

    # Metadata
    last_played: str = ""

    # Calendar constants (class-level, not instance fields)
    DAYS_PER_WEEK = 7
    WEEKS_PER_MONTH = 4
    MONTHS_PER_SEASON = 3
    DAY_NAMES = ["Moonday", "Tirdsday", "Wodensday", "Thorsday", "Freyday", "Saturnday", "Solday"]

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().strftime("%Y-%m-%d")
        if not self.last_played:
            self.last_played = datetime.now().strftime("%Y-%m-%d %H:%M")

    def to_dict(self) -> dict:
        """Serialize to dictionary for saving."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "GameState":
        """Deserialize from dictionary when loading."""
        known = cls.__dataclass_fields__
        # Filter out constants that might have been serialized
        filtered = {k: v for k, v in data.items() if k in known}
        return cls(**filtered)

    def advance_day(self):
        """Advance time by one day through the full calendar hierarchy."""
        seasons = ["Spring", "Summer", "Autumn", "Winter"]

        self.day += 1
        if self.day > self.DAYS_PER_WEEK:
            self.day = 1
            self.week += 1
            if self.week > self.WEEKS_PER_MONTH:
                self.week = 1
                self.month += 1
                if self.month > self.MONTHS_PER_SEASON:
                    self.month = 1
                    idx = seasons.index(self.season)
                    self.season = seasons[(idx + 1) % 4]
                    if self.season == "Spring":
                        self.year += 1

        self.last_played = datetime.now().strftime("%Y-%m-%d %H:%M")

    @property
    def total_days(self) -> int:
        """Total days elapsed since game start (for save display)."""
        season_idx = ["Spring", "Summer", "Autumn", "Winter"].index(self.season)
        days_per_season = self.DAYS_PER_WEEK * self.WEEKS_PER_MONTH * self.MONTHS_PER_SEASON
        return ((self.year - 1) * 4 + season_idx) * days_per_season + \
               (self.month - 1) * self.WEEKS_PER_MONTH * self.DAYS_PER_WEEK + \
               (self.week - 1) * self.DAYS_PER_WEEK + \
               (self.day - 1)

    @property
    def date_string(self) -> str:
        """Human-readable date string."""
        return f"{self.DAY_NAMES[self.day - 1]}, Week {self.week}, Month {self.month}, {self.season}, Year {self.year}"

    @property
    def short_date(self) -> str:
        """Short date for HUD display."""
        return f"📅 {self.DAY_NAMES[self.day - 1][:3]}, W{self.week} M{self.month}, {self.season[:3]} Y{self.year}"

    # --- Inventory helpers ---

    @property
    def inventory_weight(self) -> int:
        """Total weight of all items in player inventory."""
        return sum(i.get("weight", 1) * i.get("quantity", 0) for i in self.inventory)

    @property
    def inventory_free_space(self) -> int:
        """Remaining weight capacity in player inventory."""
        return max(0, self.inventory_capacity - self.inventory_weight)

    @property
    def warehouse_weight(self) -> int:
        """Total weight of all items in warehouse."""
        return sum(i.get("weight", 1) * i.get("quantity", 0) for i in self.warehouse)

    @property
    def warehouse_free_space(self) -> int:
        """Remaining weight capacity in warehouse."""
        return max(0, self.warehouse_capacity - self.warehouse_weight)

    def inventory_item(self, item_id: str) -> dict | None:
        """Find an item in player inventory by ID."""
        for i in self.inventory:
            if i["item_id"] == item_id:
                return i
        return None

    def warehouse_item(self, item_id: str) -> dict | None:
        """Find an item in warehouse by ID."""
        for i in self.warehouse:
            if i["item_id"] == item_id:
                return i
        return None

    # --- Citizen helpers ---

    @property
    def avg_need_fulfillment(self) -> float:
        """Average of all need fulfillment levels."""
        needs = [self.food_supply, self.clothing_supply, self.tools_supply,
                 self.housing_supply, self.luxury_supply]
        return sum(needs) / len(needs)

    @property
    def population_capacity(self) -> int:
        """Max population based on housing."""
        return int(self.population * (self.housing_supply / 100) * 1.5)
