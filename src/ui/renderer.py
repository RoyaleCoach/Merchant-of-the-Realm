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
    from src.systems.season_effects import get_season_icon
    season_icon = get_season_icon(state.season)
    header.add_row(
        f"🏰 {state.town_name}, {state.kingdom_name}",
        f"💰 {state.gold}g  🎒 {state.inventory_weight}/{state.inventory_capacity}  👥 {state.population}  😊{state.happiness}  {state.short_date}  {season_icon}{state.season[:3]}  {state.weather}",
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
    table.add_row("npc <name>", "View NPC detailed profile")
    table.add_row("recruit/hire <n> <bld>", "Assign NPC to a building")
    table.add_row("dismiss/fire <name>", "Remove NPC from workplace")
    table.add_row("payroll", "View workforce summary & costs")
    table.add_row("workers [building]", "View workers (all or per building)")
    table.add_row("buildings", "List town buildings")
    table.add_row("building <id>", "View building details")
    table.add_row("build [id]", "Construct a building (or list available)")
    table.add_row("upgrade <id>", "Upgrade a building level")
    table.add_row("demolish <id>", "Demolish a building (50% refund)")
    table.add_row("production (prod)", "View daily production report")
    table.add_row("supply", "View supply chain status & bottlenecks")
    table.add_row("citizens (civ)", "View population, happiness, crime, needs")
    table.add_row("weather (w)", "View current weather, season, and effects")
    table.add_row("events (ev)", "View event history and statistics")
    table.add_row("choose <n>", "Make a choice during a major event")
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
    """Display town NPCs with employment status."""
    if not state.npcs:
        console.print("[dim]No NPCs in town.[/dim]")
        return

    table = Table(title="[bold]Town NPCs[/bold]", border_style="yellow")
    table.add_column("Name", style="cyan")
    table.add_column("Profession", style="green")
    table.add_column("Gold", justify="right", style="yellow")
    table.add_column("Mood", justify="center")
    table.add_column("Workplace", style="dim")

    for n in sorted(state.npcs, key=lambda x: x["name"]):
        mood_icon = {"Happy": "😊", "Content": "🙂", "Neutral": "😐", "Worried": "😟", "Angry": "😠"}.get(n["mood"], "•")
        workplace = n.get("workplace", "—")
        if workplace and workplace != "—":
            # Find building name
            workplace_name = workplace
            for b in state.buildings:
                if b["building_id"] == workplace:
                    workplace_name = b["name"]
                    break
        else:
            workplace_name = "[dim]Unemployed[/dim]"
        table.add_row(n["name"], n["profession"], f"{n['gold']}g", f"{mood_icon} {n['mood']}", workplace_name)

    console.print(table)
    console.print("[dim]Use 'npc <name>' for detailed info. 'recruit <name> <building>' to hire.[/dim]")


def show_npc_detail(info: dict):
    """Display detailed NPC information."""
    # Header
    console.print(Panel(
        f"[bold]{info['name']}[/bold] — {info['profession']}, Age {info['age']}\n"
        f"{info['mood_icon']} {info['mood']} | 💰 {info['gold']}g",
        title="[bold]👤 NPC Profile[/bold]",
        border_style="yellow",
    ))

    # Attributes table
    def attr_style(value: int) -> str:
        if value >= 70:
            return "green"
        elif value >= 40:
            return "dim"
        else:
            return "red"

    attrs = Table(show_header=False, box=None, padding=(0, 2))
    attrs.add_column("Attribute", style="cyan", width=14)
    attrs.add_column("Value", justify="right")
    attrs.add_column("Label", style="dim")
    attrs.add_row("Loyalty", str(info["loyalty"]), f"[{attr_style(info['loyalty'])}]{info['loyalty_label']}[/{attr_style(info['loyalty'])}]")
    attrs.add_row("Greed", str(info["greed"]), f"[{attr_style(100 - info['greed'])}]{info['greed_label']}[/{attr_style(100 - info['greed'])}]")
    attrs.add_row("Reputation", str(info["reputation"]), f"[{attr_style(info['reputation'])}]{info['rep_label']}[/{attr_style(info['reputation'])}]")
    attrs.add_row("Relationship", str(info["relationship"]), f"[{attr_style(info['relationship'])}]{info['rel_label']}[/{attr_style(info['relationship'])}]")
    console.print(Panel(attrs, title="[bold]Attributes[/bold]", border_style="dim"))

    # Workplace
    if info["workplace"]:
        console.print(f"[dim]Works at: {info['workplace']}[/dim]")
    else:
        console.print("[dim]Currently unemployed — use 'recruit <name> <building>' to hire.[/dim]")


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


def show_building_info(info: dict):
    """Display detailed building information."""
    if not info:
        console.print("[red]Building not found.[/red]")
        return

    # Header with level
    level_str = f"Level {info['level']}/{info['max_level']}"
    console.print(Panel(
        f"[bold]{info['name']}[/bold] — {level_str}\n"
        f"[dim]{info['description']}[/dim]",
        title="[bold]🏗️ Building Info[/bold]",
        border_style="yellow",
    ))

    # Stats table
    stats = Table(show_header=False, box=None, padding=(0, 2))
    stats.add_column("Label", style="cyan", width=16)
    stats.add_column("Value")
    stats.add_row("Workers", f"{info['workers']}/{info['max_workers']}")
    stats.add_row("Efficiency", f"{info['efficiency']*100:.0f}%")
    stats.add_row("Maintenance", f"{info['maintenance']}g/day")
    if info["produces"]:
        stats.add_row("Produces", info["produces"].capitalize())
    if info["requires"]:
        stats.add_row("Requires", info["requires"].capitalize())
    console.print(Panel(stats, title="[bold]Stats[/bold]", border_style="dim"))

    # Actions
    actions = Table(show_header=False, box=None, padding=(0, 2))
    actions.add_column("Action", style="cyan", width=16)
    actions.add_column("Cost")
    if info["level"] < info["max_level"]:
        actions.add_row("Upgrade", f"{info['upgrade_cost']}g")
    else:
        actions.add_row("Upgrade", "[dim]Max level reached[/dim]")
    actions.add_row("Demolish", f"[green]+{info['demolish_refund']}g refund[/green]")
    console.print(Panel(actions, title="[bold]Actions[/bold]", border_style="green"))


def show_constructible(state: GameState):
    """Display buildings available to construct."""
    from src.economy.buildings import get_constructible_buildings

    available = get_constructible_buildings(state)
    if not available:
        console.print("[dim]All building types have been constructed.[/dim]")
        return

    table = Table(title="[bold]🔨 Available Buildings[/bold]", border_style="yellow")
    table.add_column("ID", style="cyan", width=14)
    table.add_column("Building")
    table.add_column("Cost", justify="right", style="yellow")
    table.add_column("Max Workers", justify="right", style="green")
    table.add_column("Description", style="dim")

    for b in sorted(available, key=lambda x: x["cost"]):
        table.add_row(
            b["building_id"],
            b["name"],
            f"{b['cost']}g",
            str(b["max_workers"]),
            b.get("description", ""),
        )

    console.print(table)
    console.print(f"[dim]Gold: {state.gold}g | Use 'build <building_id>' to construct.[/dim]")


def show_production_report(report: list[dict], buildings: list[dict], weather_mod: float):
    """Display daily production report."""
    if not report:
        console.print("[dim]No buildings are producing anything.[/dim]")
        return

    # Header
    if weather_mod < 1.0:
        console.print(f"[dim]Weather production modifier: {weather_mod*100:.0f}%[/dim]")

    # Group by supply chain
    chained = [r for r in report if r["is_in_chain"]]
    standalone = [r for r in report if not r["is_in_chain"]]
    idle = [b for b in buildings if not any(r["building_id"] == b["building_id"] for r in report)]

    if chained:
        table = Table(title="[bold]⚙️ Supply Chains[/bold]", border_style="yellow")
        table.add_column("Chain")
        table.add_column("Output", justify="right", style="green")
        table.add_column("Workers", justify="center", style="cyan")
        table.add_column("Efficiency", justify="right", style="dim")

        shown = set()
        for r in chained:
            key = r["building_id"]
            if key in shown:
                continue
            shown.add(key)

            # Build chain display
            chain_str = r["name"]
            if r["requires_name"] and r["input_source"]:
                chain_str = f"{r['input_source']} → {r['name']}"

            eff_pct = f"{r['efficiency']*100:.0f}%"
            workers_str = f"{r['workers']}/{r['max_workers']}"

            table.add_row(
                chain_str,
                f"{r['output']}x {r['produces_name']}",
                workers_str,
                eff_pct,
            )

        console.print(table)

    if standalone:
        table = Table(title="[bold]🏭 Standalone Production[/bold]", border_style="yellow")
        table.add_column("Building")
        table.add_column("Output", justify="right", style="green")
        table.add_column("Workers", justify="center", style="cyan")
        table.add_column("Efficiency", justify="right", style="dim")

        for r in standalone:
            eff_pct = f"{r['efficiency']*100:.0f}%"
            workers_str = f"{r['workers']}/{r['max_workers']}"
            table.add_row(
                r["name"],
                f"{r['output']}x {r['produces_name']}",
                workers_str,
                eff_pct,
            )

        console.print(table)

    if idle:
        idle_names = ", ".join(b["name"] for b in idle)
        console.print(f"[dim]Idle (no workers): {idle_names}[/dim]")

    # Summary
    total_output = sum(r["output"] for r in report)
    total_workers = sum(r["workers"] for r in report)
    console.print(
        f"[dim]Total: {total_output} items/day | "
        f"{total_workers} workers employed[/dim]"
    )


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


def show_workforce_summary(summary: dict):
    """Display workforce summary."""
    if summary["total_workers"] == 0:
        console.print("[dim]No workers employed.[/dim]")
        return

    console.print(Panel(
        f"[bold]Total Workers:[/bold] {summary['total_workers']}\n"
        f"[bold]Buildings Staffed:[/bold] {summary['buildings_staffed']}\n"
        f"[bold]Daily Payroll:[/bold] [yellow]{summary['total_payroll']}g[/yellow]\n"
        f"[bold]Avg Skill:[/bold] {summary['avg_skill']:.1f}/10  "
        f"[bold]Avg Morale:[/bold] {summary['avg_morale']:.0f}/100  "
        f"[bold]Avg Health:[/bold] {summary['avg_health']:.0f}/100",
        title="[bold]👷 Workforce Overview[/bold]",
        border_style="yellow",
    ))


def show_workers(workers: list[dict], building_id: str, state: GameState):
    """Display workers at a building."""
    if not workers:
        console.print(f"[dim]No workers at {building_id}.[/dim]")
        return

    # Find building name
    building_name = building_id
    for b in state.buildings:
        if b["building_id"] == building_id:
            building_name = b["name"]
            break

    table = Table(title=f"[bold]👷 Workers at {building_name}[/bold]", border_style="yellow")
    table.add_column("Name", style="cyan")
    table.add_column("Profession", style="green")
    table.add_column("Skill", justify="center", style="yellow")
    table.add_column("Morale", justify="center")
    table.add_column("Health", justify="center", style="dim")
    table.add_column("Salary", justify="right", style="yellow")
    table.add_column("Exp", justify="right", style="dim")

    for w in sorted(workers, key=lambda x: x["name"]):
        morale = w.get("morale", 50)
        if morale >= 70:
            morale_style = "green"
        elif morale >= 40:
            morale_style = "dim"
        else:
            morale_style = "red"

        health = w.get("health", 100)
        if health >= 70:
            health_style = "green"
        elif health >= 40:
            health_style = "yellow"
        else:
            health_style = "red"

        table.add_row(
            w["name"],
            w.get("profession", "—"),
            f"{w.get('skill', 1)}/10",
            f"[{morale_style}]{morale}[/{morale_style}]",
            f"[{health_style}]{health}[/{health_style}]",
            f"{w.get('salary', 10)}g",
            str(w.get("experience", 0)),
        )

    console.print(table)


def show_supply_chains(chains: list[dict], summary: dict):
    """Display supply chain analysis."""
    # Summary header
    health_summary = (
        f"[green]{summary['healthy']} healthy[/green] | "
        f"[yellow]{summary['strained']} strained[/yellow] | "
        f"[red]{summary['broken']} broken[/red] | "
        f"[dim]{summary['idle']} idle[/dim]"
    )
    console.print(Panel(
        f"{summary['total_chains']} supply chains — {health_summary}",
        title="[bold]🔗 Supply Chain Status[/bold]",
        border_style="yellow",
    ))

    if summary["bottlenecks"]:
        bn = ", ".join(summary["bottlenecks"])
        console.print(f"[red]⚠ Bottlenecks: {bn}[/red]")

    # Each chain
    for i, chain in enumerate(chains):
        health = chain["health"]
        if health == "healthy":
            health_icon = "[green]✓[/green]"
        elif health == "strained":
            health_icon = "[yellow]⚡[/yellow]"
        elif health == "broken":
            health_icon = "[red]✗[/red]"
        else:
            health_icon = "[dim]○[/dim]"

        # Build chain display
        chain_rows = []
        for link in chain["links"]:
            status = link["status"]
            if status == "healthy":
                status_icon = "[green]●[/green]"
            elif status == "strained":
                status_icon = "[yellow]●[/yellow]"
            elif status == "broken":
                status_icon = "[red]●[/red]"
            else:
                status_icon = "[dim]○[/dim]"

            workers_str = f"{link['workers']}/{link['max_workers']}"
            row = f"{status_icon} {link['name']} ({workers_str}) → {link['output']}x {link['produces_name']}"

            if link.get("requires"):
                avail = link.get("input_available", 0)
                need = link.get("input_need", 0)
                if need > 0:
                    pct = (avail / need) * 100
                    row += f" [dim](input: {avail}/{need}, {pct:.0f}%)[/dim]"

            chain_rows.append(row)

        chain_text = "\n".join(chain_rows)
        if chain["bottleneck"]:
            chain_text += f"\n[red]  ↳ Bottleneck: {chain['bottleneck']}[/red]"

        console.print(Panel(
            chain_text,
            title=f"{health_icon} Chain {i + 1}",
            border_style="dim",
        ))


def show_citizens(status: dict):
    """Display citizen simulation status."""
    # Header panel
    console.print(Panel(
        f"[bold]Population:[/bold] {status['population']}  "
        f"[bold]Happiness:[/bold] [{status['happiness_color']}]{status['happiness']}/100 ({status['happiness_label']})[/{status['happiness_color']}]  "
        f"[bold]Crime:[/bold] [{status['crime_color']}]{status['crime']}/100 ({status['crime_label']})[/{status['crime_color']}]  "
        f"[bold]Trend:[/bold] [{status['migration_color']}]{status['migration_label']}[/{status['migration_color']}]",
        title="[bold]👥 Citizens[/bold]",
        border_style="yellow",
    ))

    # Needs table
    table = Table(title="[bold]Need Fulfillment[/bold]", border_style="yellow")
    table.add_column("Need", style="cyan")
    table.add_column("Fulfillment", justify="right")
    table.add_column("Status", justify="center", width=20)

    for name, value, icon in status["needs"]:
        if value >= 70:
            bar_style = "green"
            label = "Well supplied"
        elif value >= 40:
            bar_style = "yellow"
            label = "Adequate"
        elif value >= 20:
            bar_style = "red"
            label = "Shortage"
        else:
            bar_style = "red"
            label = "Critical!"

        bar = "█" * (value // 10) + "░" * (10 - value // 10)
        table.add_row(f"{icon} {name}", f"{value}%", f"[{bar_style}]{bar}[/{bar_style}] {label}")

    console.print(table)

    # Average
    avg = status["avg_fulfillment"]
    if avg >= 60:
        avg_style = "green"
    elif avg >= 40:
        avg_style = "yellow"
    else:
        avg_style = "red"
    console.print(f"[dim]Average fulfillment: [{avg_style}]{avg:.0f}%[/{avg_style}][/dim]")


def show_weather(state: GameState, effects: list[dict]):
    """Display current weather, season, and active effects."""
    from src.systems.season_effects import get_season_icon, get_season_description

    season_icon = get_season_icon(state.season)
    season_desc = get_season_description(state.season)

    # Header: season + weather
    console.print(Panel(
        f"{season_icon} [bold]{state.season}[/bold] — {state.weather} {_weather_icon(state)}"
        f"\n[dim]{season_desc}[/dim]",
        title="[bold]🌤️ Weather & Seasons[/bold]",
        border_style="yellow",
    ))

    # Active effects table
    if effects:
        table = Table(title="[bold]Active Effects[/bold]", border_style="dim")
        table.add_column("Type", style="cyan", width=10)
        table.add_column("Name", width=14)
        table.add_column("Description")

        for eff in effects:
            if eff["type"] == "season":
                # Show per-category modifiers
                mods = eff.get("modifiers", {})
                mod_strs = []
                for cat, val in mods.items():
                    if val > 1.0:
                        mod_strs.append(f"[green]{cat}: +{int((val-1)*100)}%[/green]")
                    elif val < 1.0:
                        mod_strs.append(f"[red]{cat}: {int((val-1)*100)}%[/red]")
                    else:
                        mod_strs.append(f"{cat}: —")
                table.add_row(
                    eff["icon"] + " Season",
                    eff["name"],
                    " | ".join(mod_strs),
                )
            elif eff["type"] == "weather":
                prod = eff.get("production_mod", 1.0)
                mood = eff.get("mood_mod", 0)
                parts = []
                if prod != 1.0:
                    if prod > 1.0:
                        parts.append(f"[green]Production +{int((prod-1)*100)}%[/green]")
                    else:
                        parts.append(f"[red]Production {int((prod-1)*100)}%[/red]")
                if mood != 0:
                    if mood > 0:
                        parts.append(f"[green]Mood +{mood}[/green]")
                    else:
                        parts.append(f"[red]Mood {mood}[/red]")
                if not parts:
                    parts.append("[dim]No effect[/dim]")
                table.add_row(
                    eff["icon"] + " Weather",
                    eff["name"],
                    ", ".join(parts),
                )

        console.print(table)

    # Calendar reminder
    days_left = _days_until_season_end(state)
    console.print(f"[dim]{days_left} days remaining in {state.season}.[/dim]")


def _weather_icon(state: GameState) -> str:
    """Get the icon for current weather."""
    from src.utils.data_loader import load_data
    weather_data = load_data("weather.json")
    for wt in weather_data.get("types", []):
        if wt["name"] == state.weather:
            return wt.get("icon", "")
    return ""


def _days_until_season_end(state: GameState) -> int:
    """Calculate days remaining in the current season."""
    # Each season = 3 months * 4 weeks * 7 days = 84 days
    days_per_season = GameState.DAYS_PER_WEEK * GameState.WEEKS_PER_MONTH * GameState.MONTHS_PER_SEASON
    day_of_season = ((state.month - 1) * GameState.WEEKS_PER_MONTH * GameState.DAYS_PER_WEEK +
                     (state.week - 1) * GameState.DAYS_PER_WEEK +
                     (state.day - 1))
    return days_per_season - day_of_season


def show_event_log(log: list[dict], summary: dict):
    """Display event history and summary."""
    # Summary header
    console.print(Panel(
        f"Total events: [bold]{summary['total']}[/bold]  "
        f"[green]Positive: {summary.get('positive', 0)}[/green]  "
        f"[red]Negative: {summary.get('negative', 0)}[/red]  "
        f"[yellow]Disasters: {summary.get('disaster', 0)}[/yellow]  "
        f"[blue]Opportunities: {summary.get('opportunity', 0)}[/blue]",
        title="[bold]📜 Event Log[/bold]",
        border_style="yellow",
    ))

    if not log:
        console.print("[dim]No events recorded yet.[/dim]")
        return

    # Recent events table
    table = Table(title="[bold]Recent Events[/bold]", border_style="dim")
    table.add_column("Day", style="dim", width=6)
    table.add_column("Date", style="cyan", width=22)
    table.add_column("Event")

    for entry in reversed(log[-15:]):
        etype = entry.get("type", "neutral")
        if etype == "positive":
            icon = "[green]✦[/green]"
        elif etype == "negative":
            icon = "[red]✗[/red]"
        elif etype == "disaster":
            icon = "[red]⚠[/red]"
        elif etype == "opportunity":
            icon = "[blue]★[/blue]"
        else:
            icon = "[dim]·[/dim]"

        table.add_row(
            str(entry["day"]),
            entry["date"],
            f"{icon} {entry['text']}",
        )

    console.print(table)


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
