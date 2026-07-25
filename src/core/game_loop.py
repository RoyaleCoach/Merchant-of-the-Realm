"""Game loop — the main interactive session."""

from src.core.command_parser import parse
from src.core.config import DEFAULT_STARTING_GOLD, DEFAULT_TOWN_POPULATION
from src.core.game_state import GameState
from src.core.logger import get_logger
from src.core.save_manager import save_game, load_game, list_saves
from src.systems.tick_system import tick
from src.ui.renderer import (
    show_hud, show_messages, show_help, show_status,
    show_prompt, show_save_list, console,
)

log = get_logger(__name__)


def create_new_game() -> GameState:
    """Set up a new game world."""
    console.print()
    player_name = console.input("[cyan]Your name, merchant? [/cyan]").strip() or "Merchant"
    town_name = console.input("[cyan]Name your town? [/cyan]").strip() or "Ashvale"
    kingdom_name = console.input("[cyan]Name the kingdom? [/cyan]").strip() or "Eldoria"

    state = GameState(
        name=town_name,
        kingdom_name=kingdom_name,
        town_name=town_name,
        population=DEFAULT_TOWN_POPULATION,
        gold=DEFAULT_STARTING_GOLD,
        player_name=player_name,
    )

    console.print(f"\n[green]Welcome, {player_name}![/green]")
    console.print(f"You arrive in [yellow]{town_name}[/yellow], a small settlement in the kingdom of [yellow]{kingdom_name}[/yellow].")
    console.print(f"Your starting treasury: [yellow]{state.gold} gold[/yellow]. Your town has [yellow]{state.population}[/yellow] souls.")
    console.print("[dim]Type 'help' for commands, 'next' to advance time.[/dim]\n")

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
