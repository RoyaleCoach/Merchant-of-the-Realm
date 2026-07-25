"""Medieval Market Tycoon — Entry point."""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.core.config import DEFAULT_STARTING_GOLD
from src.core.save_manager import ensure_save_dir, list_saves

app = typer.Typer(
    no_args_is_help=True,
    add_completion=False,
    help="🏰 Medieval Market Tycoon — Build your trading empire!",
)
console = Console()


def show_banner():
    """Display the game banner."""
    banner = """
[bold yellow]⚔️  MEDIEVAL MARKET TYCOON  ⚔️[/bold yellow]
[dim]Build your trading empire from scratch[/dim]
    """
    console.print(Panel(banner, border_style="yellow"))


@app.command()
def play():
    """Start a new game."""
    show_banner()
    console.print("[green]Welcome, merchant![/green] Your adventure begins...")
    console.print(f"Starting gold: [yellow]{DEFAULT_STARTING_GOLD}[/yellow]")
    console.print("[dim]Phase 0 — Core foundation ready.[/dim]")


@app.command()
def load(slot: str = typer.Argument(..., help="Save slot name")):
    """Load a saved game."""
    show_banner()
    from src.core.save_manager import load_game
    data = load_game(slot)
    if data:
        console.print(f"[green]Loaded save '{slot}'[/green]")
    else:
        console.print(f"[red]Save '{slot}' not found.[/red]")


@app.command()
def saves():
    """List all saved games."""
    ensure_save_dir()
    save_list = list_saves()
    if not save_list:
        console.print("[dim]No saves found. Start a new game with 'play'![/dim]")
        return
    table = Table(title="Saved Games", border_style="yellow")
    table.add_column("Slot", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Date", style="dim")
    table.add_column("Gold", justify="right", style="yellow")
    for s in save_list:
        table.add_row(s["slot"], s["name"], s["date"], str(s["gold"]))
    console.print(table)


@app.command()
def version():
    """Show game version."""
    console.print("[bold]Medieval Market Tycoon[/bold] — Phase 0 (Foundation)")


if __name__ == "__main__":
    app()
