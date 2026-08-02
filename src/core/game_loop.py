"""Game loop — the main interactive session."""

from src.core.command_parser import parse
from src.core.game_state import GameState
from src.core.logger import get_logger
from src.core.save_manager import save_game, load_game, list_saves
from src.systems.tick_system import tick
from src.systems.production import generate_production_report
from src.systems.daily_updates import get_weather_mod
from src.systems.season_effects import get_active_effects, roll_season_event
from src.systems.supply_chain import analyze_supply_chain, get_chain_summary
from src.systems.citizens import get_citizen_status
from src.systems.npc_system import get_npc, get_npc_info, recruit, dismiss, get_available_npcs
from src.systems.workforce import get_workforce_summary, get_workers_at_building, get_total_payroll
from src.economy.inventory import buy, sell, deposit, withdraw
from src.economy.trading import inspect_item, get_affordability, get_profitability
from src.economy.buildings import (
    build, upgrade, demolish,
    get_constructible_buildings, get_building_info,
)
from src.ui.renderer import (
    show_hud, show_messages, show_help, show_status,
    show_prompt, show_save_list, show_world_intro,
    show_market, show_npcs, show_buildings,
    show_inventory, show_warehouse, show_inspect,
    show_building_info, show_constructible,
    show_production_report, show_npc_detail,
    show_workforce_summary, show_workers,
    show_supply_chains, show_citizens, show_weather, console,
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

            case "inspect":
                if cmd.args:
                    item_id = cmd.args[0]
                    item_data = inspect_item(state, item_id)
                    if item_data:
                        afford = get_affordability(state, item_id)
                        profit = get_profitability(state, item_id)
                        show_inspect(item_data, afford, profit)
                    else:
                        console.print(f"[red]Item '{item_id}' not found on the market.[/red]")
                else:
                    console.print("[dim]Usage: inspect <item_id>[/dim]")

            case "npcs":
                show_npcs(state)

            case "npc":
                if cmd.args:
                    npc = get_npc(state, " ".join(cmd.args))
                    if npc:
                        info = get_npc_info(npc)
                        show_npc_detail(info)
                    else:
                        console.print(f"[red]NPC not found.[/red]")
                else:
                    console.print("[dim]Usage: npc <name>[/dim]")

            case "recruit":
                if len(cmd.args) >= 2:
                    building_id = cmd.args[-1]
                    npc_name = " ".join(cmd.args[:-1])
                    console.print(recruit(state, npc_name, building_id))
                else:
                    available = get_available_npcs(state)
                    if available:
                        names = ", ".join(n["name"] for n in available)
                        console.print(f"[dim]Unemployed: {names}[/dim]")
                    else:
                        console.print("[dim]All NPCs are employed.[/dim]")
                    console.print("[dim]Usage: recruit <npc_name> <building_id>[/dim]")

            case "dismiss":
                if cmd.args:
                    console.print(dismiss(state, " ".join(cmd.args)))
                else:
                    console.print("[dim]Usage: dismiss <npc_name>[/dim]")

            case "hire":
                if len(cmd.args) >= 2:
                    building_id = cmd.args[-1]
                    npc_name = " ".join(cmd.args[:-1])
                    console.print(recruit(state, npc_name, building_id))
                else:
                    console.print("[dim]Usage: hire <npc_name> <building_id>[/dim]")

            case "fire":
                if cmd.args:
                    console.print(dismiss(state, " ".join(cmd.args)))
                else:
                    console.print("[dim]Usage: fire <npc_name>[/dim]")

            case "payroll":
                summary = get_workforce_summary(state)
                show_workforce_summary(summary)

            case "workers":
                if cmd.args:
                    workers = get_workers_at_building(state, cmd.args[0])
                    show_workers(workers, cmd.args[0], state)
                else:
                    # Show all workers across all buildings
                    for b in state.buildings:
                        workers = get_workers_at_building(state, b["building_id"])
                        if workers:
                            show_workers(workers, b["building_id"], state)

            case "buildings":
                show_buildings(state)

            case "build":
                if cmd.args:
                    console.print(build(state, cmd.args[0]))
                else:
                    show_constructible(state)

            case "upgrade":
                if cmd.args:
                    console.print(upgrade(state, cmd.args[0]))
                else:
                    console.print("[dim]Usage: upgrade <building_id>[/dim]")

            case "demolish":
                if cmd.args:
                    console.print(demolish(state, cmd.args[0]))
                else:
                    console.print("[dim]Usage: demolish <building_id>[/dim]")

            case "building":
                if cmd.args:
                    for b in state.buildings:
                        if b["building_id"] == cmd.args[0]:
                            info = get_building_info(b)
                            show_building_info(info)
                            break
                    else:
                        console.print(f"[red]Building '{cmd.args[0]}' not found.[/red]")
                else:
                    console.print("[dim]Usage: building <building_id>[/dim]")

            case "production" | "prod":
                weather_mod = get_weather_mod(state)
                report = generate_production_report(state, weather_mod)
                show_production_report(report, state.buildings, weather_mod)

            case "supply":
                weather_mod = get_weather_mod(state)
                chains = analyze_supply_chain(state, weather_mod)
                summary = get_chain_summary(state, weather_mod)
                show_supply_chains(chains, summary)

            case "citizens" | "civ":
                status = get_citizen_status(state)
                show_citizens(status)

            case "weather" | "w":
                effects = get_active_effects(state)
                show_weather(state, effects)

            case "inventory" | "inv":
                show_inventory(state)

            case "warehouse" | "wh":
                show_warehouse(state)

            case "buy":
                if len(cmd.args) >= 2:
                    item_id = cmd.args[0]
                    try:
                        qty = int(cmd.args[1])
                    except ValueError:
                        console.print("[red]Invalid quantity.[/red]")
                        continue
                    console.print(buy(state, item_id, qty))
                else:
                    console.print("[dim]Usage: buy <item_id> <quantity>[/dim]")

            case "sell":
                if len(cmd.args) >= 2:
                    item_id = cmd.args[0]
                    try:
                        qty = int(cmd.args[1])
                    except ValueError:
                        console.print("[red]Invalid quantity.[/red]")
                        continue
                    console.print(sell(state, item_id, qty))
                else:
                    console.print("[dim]Usage: sell <item_id> <quantity>[/dim]")

            case "deposit" | "dep":
                if len(cmd.args) >= 2:
                    item_id = cmd.args[0]
                    try:
                        qty = int(cmd.args[1])
                    except ValueError:
                        console.print("[red]Invalid quantity.[/red]")
                        continue
                    console.print(deposit(state, item_id, qty))
                else:
                    console.print("[dim]Usage: deposit <item_id> <quantity>[/dim]")

            case "withdraw" | "wd":
                if len(cmd.args) >= 2:
                    item_id = cmd.args[0]
                    try:
                        qty = int(cmd.args[1])
                    except ValueError:
                        console.print("[red]Invalid quantity.[/red]")
                        continue
                    console.print(withdraw(state, item_id, qty))
                else:
                    console.print("[dim]Usage: withdraw <item_id> <quantity>[/dim]")

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
