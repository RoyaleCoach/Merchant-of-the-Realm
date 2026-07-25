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

    # Player
    player_name: str = ""

    # World entities (stored as dicts for JSON serialization)
    market: list[dict] = field(default_factory=list)
    npcs: list[dict] = field(default_factory=list)
    buildings: list[dict] = field(default_factory=list)

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
