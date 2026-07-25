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
        f"💰 {state.gold}g  {state.short_date}  👥 {state.population}  {state.weather}",
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
    table.add_row("status", "Show kingdom status")
    table.add_row("market", "View market prices")
    table.add_row("npcs", "List town NPCs")
    table.add_row("buildings", "List town buildings")
    table.add_row("save [slot]", "Save the game")
    table.add_row("load [slot]", "Load a saved game")
    table.add_row("quit", "Return to main menu")
    table.add_row("help", "Show this help message")
    console.print(table)


def show_status(state: GameState):
    """Display detailed kingdom status."""
    table = Table(title="[bold]Kingdom Status[/bold]", border_style="yellow")
    table.add_column("Property", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Kingdom", state.kingdom_name)
    table.add_row("Town", state.town_name)
    table.add_row("Population", str(state.population))
    table.add_row("Weather", state.weather)
    table.add_row("Date", state.date_string)
    table.add_row("Day Total", f"{state.total_days} days elapsed")
    table.add_row("Gold", f"{state.gold}g")
    table.add_row("Player", state.player_name)
    table.add_row("Market Items", str(len(state.market)))
    table.add_row("NPCs", str(len(state.npcs)))
    table.add_row("Buildings", str(len(state.buildings)))
    console.print(table)


def show_world_intro(state: GameState, world):
    """Display the new game world introduction."""
    console.print()
    console.print(f"[green]Welcome, {state.player_name}![/green]")
    console.print(
        f"You arrive in [yellow]{state.town_name}[/yellow], "
        f"a settlement of [yellow]{state.population}[/yellow] souls "
        f"in the kingdom of [yellow]{state.kingdom_name}[/yellow]."
    )
    console.print(f"The weather is [yellow]{state.weather}[/yellow]. Your treasury: [yellow]{state.gold} gold[/yellow].")
    console.print()

    # Show starting buildings
    if world.buildings:
        bldg_table = Table(show_header=False, box=None, padding=(0, 1))
        bldg_table.add_column("Icon", width=3)
        bldg_table.add_column("Building")
        for b in world.buildings:
            bldg_table.add_row("🏗️", f"{b.name} (Level {b.level})")
        console.print(Panel(bldg_table, title="[bold]Starting Buildings[/bold]", border_style="dim"))

    # Show a few NPCs
    if world.npcs:
        npc_names = ", ".join(n.name for n in world.npcs[:5])
        extra = f" and {len(world.npcs) - 5} more" if len(world.npcs) > 5 else ""
        console.print(f"[dim]Notable figures: {npc_names}{extra}[/dim]")

    console.print("[dim]Type 'help' for commands, 'next' to advance time.[/dim]")
    console.print()


def show_market(state: GameState):
    """Display current market prices."""
    if not state.market:
        console.print("[dim]No market items available.[/dim]")
        return

    table = Table(title="[bold]Market Prices[/bold]", border_style="yellow")
    table.add_column("Item", style="cyan")
    table.add_column("Category", style="dim")
    table.add_column("Price", justify="right", style="yellow")
    table.add_column("Supply", justify="right", style="green")
    table.add_column("Demand", justify="right", style="red")
    table.add_column("Trend", justify="center", width=8)

    for m in state.market:
        if m["supply"] > m["demand"]:
            trend = "↓"
            trend_style = "red"
        elif m["demand"] > m["supply"]:
            trend = "↑"
            trend_style = "green"
        else:
            trend = "─"
            trend_style = "dim"

        table.add_row(
            m["name"],
            m.get("category", "general").capitalize(),
            f"{m['current_price']}g",
            str(m["supply"]),
            str(m["demand"]),
            f"[{trend_style}]{trend}[/{trend_style}]",
        )

    console.print(table)


def show_npcs(state: GameState):
    """Display town NPCs."""
    if not state.npcs:
        console.print("[dim]No NPCs in town.[/dim]")
        return

    table = Table(title="[bold]Town NPCs[/bold]", border_style="yellow")
    table.add_column("Name", style="cyan")
    table.add_column("Profession", style="green")
    table.add_column("Gold", justify="right", style="yellow")
    table.add_column("Mood", justify="center")

    for n in state.npcs:
        mood_icon = {"Happy": "😊", "Content": "🙂", "Neutral": "😐", "Worried": "😟", "Angry": "😠"}.get(n["mood"], "•")
        table.add_row(n["name"], n["profession"], f"{n['gold']}g", f"{mood_icon} {n['mood']}")

    console.print(table)


def show_buildings(state: GameState):
    """Display town buildings."""
    if not state.buildings:
        console.print("[dim]No buildings in town.[/dim]")
        return

    table = Table(title="[bold]Town Buildings[/bold]", border_style="yellow")
    table.add_column("Building", style="cyan")
    table.add_column("Level", justify="center", style="green")
    table.add_column("Workers", justify="center", style="yellow")

    for b in state.buildings:
        table.add_row(b["name"], str(b["level"]), f"{b['workers']}/{b['max_workers']}")

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
