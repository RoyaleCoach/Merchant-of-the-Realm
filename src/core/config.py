"""Central configuration for Merchant of the Realm."""

from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SAVE_DIR = PROJECT_ROOT / "saves"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Game defaults
DEFAULT_STARTING_GOLD = 1500
DEFAULT_TOWN_POPULATION = 500
MAX_SAVE_SLOTS = 10

# Logging
LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
