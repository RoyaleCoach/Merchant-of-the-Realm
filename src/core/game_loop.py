"""Game loop — the main interactive session."""

from src.core.command_parser import parse
from src.core.game_state import GameState
from src.core.logger import get_logger
from src.core.save_manager import save_game, load_game, list_saves
from src.systems.tick_system import tick
from src.ui.renderer import (
    show_hud, show_messages, show_help, show_status,
    show_prompt, show_save_list, show_world_intro,
    show_market, show_npcs, show_buildings, console,
)
from src.world.generator import generate_world

log = get_logger(__name__)


def create_new_game() -> GameState:
    """Set up a new game world."""
    console.print()
    player_name = console.input("[cyan]Your name, merchant? [/cyan]").strip() or "Merchant"
    town_name = console.input("[cyan]Name your town (or Enter for random)? [/cyan]").strip() or None
    kingdom_name = console.input("[cyan]Name the kingdom (or Enter for random)? [/cyan]").strip() or None

    world = generate_world(
        player_name=player_name,
        town_name=town_name,
        kingdom_name=kingdom_name,
    )

    state = GameState(
        name=world.town_name,
        kingdom_name=world.kingdom_name,
        town_name=world.town_name,
        population=world.population,
        gold=world.gold,
        weather=world.weather,
        player_name=player_name,
        market=[m.__dict__ for m in world.market],
        npcs=[n.__dict__ for n in world.npcs],
        buildings=[b.__dict__ for b in world.buildings],
    )

    show_world_intro(state, world)
    return state


def run_game_loop(state: GameState):
    """Run the interactive game loop."""
    show_hud(state)

    while True:
        show_prompt()
        try:
            raw = input()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break

        cmd = parse(raw)

        match cmd.action:
            case "empty":
                continue

            case "help":
                show_help()

            case "status":
                show_status(state)

            case "market":
                show_market(state)

            case "npcs":
                show_npcs(state)

            case "buildings":
                show_buildings(state)

            case "next":
                messages = tick(state)
                show_messages(messages)
                show_hud(state)

            case "save":
                slot = cmd.args[0] if cmd.args else "quicksave"
                state.name = state.town_name
                state.last_played = __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M")
                save_game(slot, state.to_dict())
                console.print(f"[green]Game saved to '{slot}'.[/green]")

            case "load":
                if not cmd.args:
                    show_save_list(list_saves())
                    slot = console.input("[cyan]Slot to load: [/cyan]").strip()
                else:
                    slot = cmd.args[0]
                if slot:
                    data = load_game(slot)
                    if data:
                        state = GameState.from_dict(data)
                        console.print(f"[green]Loaded save '{slot}'.[/green]")
                        show_hud(state)
                    else:
                        console.print(f"[red]Save '{slot}' not found.[/red]")

            case "quit" | "exit":
                console.print("[dim]Returning to main menu...[/dim]")
                break

            case _:
                console.print(f"[red]Unknown command: '{cmd.action}'. Type 'help' for available commands.[/red]")
