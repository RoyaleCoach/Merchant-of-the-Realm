# 🏰 Medieval Market Tycoon

A CLI simulation game where you build a trading empire in a medieval kingdom.

## Stack

- **Python 3.13+**
- **Typer** — CLI framework
- **Rich** — Terminal UI (tables, panels, colors)
- **pytest** — Testing

## Quick Start

```bash
# Install dependencies
pip install -e ".[dev]"

# Run the game
python main.py play

# List saves
python main.py saves

# Load a save
python main.py load my_save

# Show version
python main.py version
```

## Development Workflow

See [workflow.md](workflow.md) for the full 24-phase roadmap.

| Milestone | Features |
|:---|:---|
| **MVP v0.1** | Menu, save/load, calendar, market, buy/sell |
| **Alpha v0.2** | Buildings, production, inventory, warehouse |
| **Alpha v0.3** | NPCs, workers, dynamic pricing, supply chains |
| **Beta v0.4** | Weather, seasons, random events, reputation |
| **Beta v0.5** | Multi-town trading, caravans, AI competitors |
| **Release v1.0** | Politics, advanced economy, endgame, achievements |

## License

MIT
