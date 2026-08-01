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
        f"💰 {state.gold}g  🎒 {state.inventory_weight}/{state.inventory_capacity}  {state.short_date}  👥 {state.population}  {state.weather}",
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
    table.add_column("Command", style="cyan", width=20)
    table.add_column("Description")
    table.add_row("next", "Advance to the next day")
    table.add_row("status", "Show kingdom status")
    table.add_row("market", "View market prices")
    table.add_row("inspect <item>", "Detailed item analysis (price, supply, demand)")
    table.add_row("npcs", "List town NPCs")
    table.add_row("buildings", "List town buildings")
    table.add_row("inventory (inv)", "View your inventory")
    table.add_row("warehouse (wh)", "View warehouse contents")
    table.add_row("buy <item> <qty>", "Buy items from the market")
    table.add_row("sell <item> <qty>", "Sell items to the market (90% value)")
    table.add_row("deposit <item> <qty>", "Move items from inventory to warehouse")
    table.add_row("withdraw <item> <qty>", "Move items from warehouse to inventory")
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

    console.print("[dim]Type 'help' for commands, 'next' to advance time, 'buy'/'sell' to trade.[/dim]")
    console.print()


def show_market(state: GameState):
    """Display current market prices with base comparison."""
    if not state.market:
        console.print("[dim]No market items available.[/dim]")
        return

    table = Table(title="[bold]Market Prices[/bold]", border_style="yellow")
    table.add_column("Item", style="cyan")
    table.add_column("Category", style="dim")
    table.add_column("Price", justify="right", style="yellow")
    table.add_column("Base", justify="right", style="dim")
    table.add_column("Diff", justify="right", width=10)
    table.add_column("Supply", justify="right", style="green")
    table.add_column("Demand", justify="right", style="red")
    table.add_column("Trend", justify="center", width=8)

    for m in sorted(state.market, key=lambda x: x["name"]):
        base = m["base_price"]
        current = m["current_price"]
        diff = current - base
        pct = ((current - base) / base) * 100 if base > 0 else 0

        if m["supply"] > m["demand"]:
            trend = "↓"
            trend_style = "red"
        elif m["demand"] > m["supply"]:
            trend = "↑"
            trend_style = "green"
        else:
            trend = "─"
            trend_style = "dim"

        if diff > 0:
            diff_str = f"[red]+{diff}g ({pct:+.0f}%)"
        elif diff < 0:
            diff_str = f"[green]{diff}g ({pct:+.0f}%)"
        else:
            diff_str = "[dim]0g (0%)[/dim]"

        table.add_row(
            m["name"],
            m.get("category", "general").capitalize(),
            f"{current}g",
            f"{base}g",
            diff_str,
            str(m["supply"]),
            str(m["demand"]),
            f"[{trend_style}]{trend}[/{trend_style}]",
        )

    console.print(table)
    console.print("[dim]Use 'inspect <item>' for detailed analysis.[/dim]")


def show_inspect(item_data: dict | None, affordability: dict | None, profitability: dict | None):
    """Display detailed inspection of a market item."""
    if item_data is None:
        console.print("[red]Item not found on the market.[/red]")
        return

    # Price panel
    if item_data["diff"] > 0:
        diff_style = "red"
        diff_label = "overpriced"
    elif item_data["diff"] < 0:
        diff_style = "green"
        diff_label = "underpriced"
    else:
        diff_style = "dim"
        diff_label = "at base price"

    price_text = (
        f"[bold]{item_data['name']}[/bold] — {item_data['category'].capitalize()}\n"
        f"Current: [yellow]{item_data['current_price']}g[/yellow]  "
        f"Base: [dim]{item_data['base_price']}g[/dim]\n"
        f"[{diff_style}]Price is {abs(item_data['pct']):.0f}% {diff_label} ({item_data['diff']:+d}g)[/{diff_style}]"
    )
    console.print(Panel(price_text, title="[bold]Price Analysis[/bold]", border_style="yellow"))

    # Supply & Demand panel
    ratio = item_data["ratio"]
    if ratio > 1.2:
        market_label = "[red]Seller's market[/red] (high demand)"
    elif ratio < 0.8:
        market_label = "[green]Buyer's market[/green] (high supply)"
    else:
        market_label = "[dim]Balanced[/dim]"

    sd_table = Table(show_header=False, box=None, padding=(0, 2))
    sd_table.add_column("Label", style="cyan", width=14)
    sd_table.add_column("Value")
    sd_table.add_row("Supply", str(item_data["supply"]))
    sd_table.add_row("Demand", str(item_data["demand"]))
    sd_table.add_row("S/D Ratio", f"{ratio:.2f}")
    sd_table.add_row("Market", market_label)
    console.print(Panel(sd_table, title="[bold]Supply & Demand[/bold]", border_style="dim"))

    # Affordability panel
    if affordability is not None:
        aff_table = Table(show_header=False, box=None, padding=(0, 2))
        aff_table.add_column("Label", style="cyan", width=18)
        aff_table.add_column("Value")
        aff_table.add_row("Your Gold", f"{affordable_text(affordability)}")
        console.print(Panel(aff_table, title="[bold]Affordability[/bold]", border_style="green"))

    # Profitability panel
    if profitability is not None:
        prof_table = Table(show_header=False, box=None, padding=(0, 2))
        prof_table.add_column("Label", style="cyan", width=18)
        prof_table.add_column("Value")
        prof_table.add_row("Owned", f"{profitability['quantity_owned']}x")
        prof_table.add_row("Sell Price", f"{profitability['sell_price']}g each")
        prof_table.add_row("Total Revenue", f"[green]{profitability['total_revenue']}g[/green]")
        console.print(Panel(prof_table, title="[bold]Sell Profit[/bold]", border_style="red"))


def affordable_text(affordability: dict) -> str:
    """Format affordability info."""
    return (
        f"Can afford [yellow]{affordability['max_affordable']}x[/yellow] "
        f"(gold allows {affordability['max_by_gold']}x, "
        f"stock: {affordability['in_stock']}x)"
    )


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


def show_inventory(state: GameState):
    """Display player inventory."""
    if not state.inventory:
        console.print("[dim]Your inventory is empty.[/dim]")
        return

    table = Table(title="[bold]🎒 Inventory[/bold]", border_style="yellow")
    table.add_column("Item", style="cyan")
    table.add_column("Quantity", justify="right", style="green")
    table.add_column("Weight", justify="right", style="dim")

    for i in sorted(state.inventory, key=lambda x: x["name"]):
        w = i.get("weight", 1) * i["quantity"]
        table.add_row(i["name"], str(i["quantity"]), f"{w}")

    console.print(table)
    console.print(
        f"[dim]Weight: {state.inventory_weight}/{state.inventory_capacity} "
        f"(free: {state.inventory_free_space})[/dim]"
    )


def show_warehouse(state: GameState):
    """Display warehouse contents."""
    if not state.warehouse:
        console.print("[dim]The warehouse is empty.[/dim]")
        return

    table = Table(title="[bold]🏚️ Warehouse[/bold]", border_style="yellow")
    table.add_column("Item", style="cyan")
    table.add_column("Quantity", justify="right", style="green")
    table.add_column("Weight", justify="right", style="dim")

    for i in sorted(state.warehouse, key=lambda x: x["name"]):
        w = i.get("weight", 1) * i["quantity"]
        table.add_row(i["name"], str(i["quantity"]), f"{w}")

    console.print(table)
    console.print(
        f"[dim]Weight: {state.warehouse_weight}/{state.warehouse_capacity} "
        f"(free: {state.warehouse_free_space})[/dim]"
    )


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
