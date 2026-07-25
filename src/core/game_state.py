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

    # Time
    day: int = 1
    season: str = "Spring"  # Spring, Summer, Autumn, Winter
    year: int = 1

    # Economy
    gold: int = 0

    # Player
    player_name: str = ""

    # Metadata
    last_played: str = ""

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
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    def advance_day(self):
        """Advance time by one day."""
        seasons = ["Spring", "Summer", "Autumn", "Winter"]
        self.day += 1
        if self.day > 30:
            self.day = 1
            idx = seasons.index(self.season)
            self.season = seasons[(idx + 1) % 4]
            if self.season == "Spring":
                self.year += 1
        self.last_played = datetime.now().strftime("%Y-%m-%d %H:%M")

    @property
    def date_string(self) -> str:
        """Human-readable date string."""
        return f"Day {self.day}, {self.season}, Year {self.year}"
