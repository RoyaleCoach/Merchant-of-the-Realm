"""Terminal rendering — all screen output goes through here."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from src.core.game_state import GameState

console = Console()


def show_banner():
    """Display the game title banner."""
    banner = Text.assemble(
        ("⚔️  ", "bold yellow"),
        ("MEDIEVAL MARKET TYCOON", "bold yellow"),
        ("  ⚔️\n", "bold yellow"),
        ("Build your trading empire from scratch", "dim"),
    )
    console.print(Panel(banner, border_style="yellow", padding=(1, 2)))


def show_main_menu():
    """Display the main menu."""
    menu = Table(show_header=False, box=None, padding=(0, 2))
    menu.add_column("Key", style="cyan bold", width=6)
    menu.add_column("Action")
    menu.add_row("1", "New Game")
    menu.add_row("2", "Load Game")
    menu.add_row("3", "Exit")
    console.print(Panel(menu, title="[bold]Main Menu[/bold]", border_style="yellow"))


def show_game_header(state: GameState):
    """Display the in-game status bar."""
    header = Table(show_header=False, box=None, expand=True)
    header.add_column("Left", style="cyan")
    header.add_column("Right", style="yellow", justify="right")
    header.add_row(
        f"🏰 {state.town_name}, {state.kingdom_name}",
        f"💰 {state.gold}g  📅 {state.date_string}  👥 {state.population}",
    )
    console.print(header)


def show_hud(state: GameState):
    """Display the full in-game HUD."""
    show_game_header(state)
    console.print()


def show_messages(messages: list[str]):
    """Display a list of event messages."""
    for msg in messages:
        console.print(f"  {msg}")


def show_help():
    """Display available commands."""
    table = Table(title="[bold]Commands[/bold]", border_style="dim", show_lines=False)
    table.add_column("Command", style="cyan", width=16)
    table.add_column("Description")
    table.add_row("next", "Advance to the next day")
    table.add_row("status", "Show current game status")
    table.add_row("save [slot]", "Save the game")
    table.add_row("load [slot]", "Load a saved game")
    table.add_row("quit", "Return to main menu")
    table.add_row("help", "Show this help message")
    console.print(table)


def show_status(state: GameState):
    """Display detailed game status."""
    table = Table(title="[bold]Kingdom Status[/bold]", border_style="yellow")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Kingdom", state.kingdom_name)
    table.add_row("Town", state.town_name)
    table.add_row("Population", str(state.population))
    table.add_row("Date", state.date_string)
    table.add_row("Gold", f"{state.gold}g")
    table.add_row("Player", state.player_name)
    console.print(table)


def show_prompt():
    """Display the command prompt."""
    console.print()
    console.print("[bold cyan]merchant→[/bold cyan] ", end="")


def show_goodbye():
    """Display exit message."""
    console.print("[dim]Farewell, merchant. Your legend awaits your return.[/dim]")


def show_save_list(saves: list[dict]):
    """Display saved games."""
    if not saves:
        console.print("[dim]No saves found.[/dim]")
        return
    table = Table(title="[bold]Saved Games[/bold]", border_style="yellow")
    table.add_column("Slot", style="cyan")
    table.add_column("Town", style="green")
    table.add_column("Date", style="dim")
    table.add_column("Gold", justify="right", style="yellow")
    for s in saves:
        table.add_row(s["slot"], s["name"], s["date"], f"{s['gold']}g")
    console.print(table)
