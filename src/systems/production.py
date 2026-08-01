"""Production system — building output, supply chains, daily production reports."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data, get_building

log = get_logger(__name__)


def get_building_output(building: dict, weather_mod: float = 1.0) -> int:
    """Calculate daily output for a single building."""
    if building["workers"] <= 0 or building["max_workers"] <= 0:
        return 0
    worker_ratio = building["workers"] / building["max_workers"]
    return int(10 * worker_ratio * weather_mod * building["level"])


def get_production_chain(building_id: str, buildings_data: dict) -> list[dict]:
    """
    Trace the production chain starting from a building.
    Returns a list of chain links: [{building, produces, requires, consumer}, ...]
    Example: Farm → Wheat → Bakery → Bread
    """
    chain = []
    visited = set()
    current_id = building_id

    while current_id and current_id not in visited:
        visited.add(current_id)
        bdata = buildings_data.get(current_id)
        if bdata is None:
            break

        link = {
            "building_id": current_id,
            "name": bdata["name"],
            "produces": bdata.get("produces"),
            "requires": bdata.get("requires"),
            "consumer_id": None,
        }

        # Find who consumes this building's output
        produces = bdata.get("produces")
        if produces:
            for bid, other in buildings_data.items():
                if other.get("requires") == produces and bid != current_id:
                    link["consumer_id"] = bid
                    link["consumer_name"] = other["name"]
                    break

        chain.append(link)

        # Follow the chain
        if link["consumer_id"]:
            current_id = link["consumer_id"]
        else:
            break

    return chain


def generate_production_report(state: GameState, weather_mod: float = 1.0) -> list[dict]:
    """
    Generate a full production report for all buildings.
    Returns a list of production entries with building, output, and chain info.
    """
    buildings_data = load_data("buildings.json")
    report = []

    for b in state.buildings:
        bdata = buildings_data.get(b["building_id"], {})
        produces = bdata.get("produces")
        requires = bdata.get("requires")

        if not produces:
            continue

        output = get_building_output(b, weather_mod)

        # Find market item name
        item_name = produces.capitalize()
        for m in state.market:
            if m["item_id"] == produces:
                item_name = m["name"]
                break

        # Find input item name
        input_name = None
        if requires:
            for m in state.market:
                if m["item_id"] == requires:
                    input_name = m["name"]
                    break

        # Check if this building is part of a chain
        # A building is in a chain if it has a consumer (someone needs its output)
        # OR if it has a producer (it needs someone else's output)
        chain_forward = get_production_chain(b["building_id"], buildings_data)
        has_consumer = any(
            other.get("requires") == produces
            for other in buildings_data.values()
        )
        is_in_chain = len(chain_forward) > 1 or has_consumer or requires is not None

        # Find the producer of our input (if any)
        input_source = None
        if requires:
            for other_b in state.buildings:
                other_data = buildings_data.get(other_b["building_id"], {})
                if other_data.get("produces") == requires:
                    input_source = other_b["name"]
                    break

        report.append({
            "building_id": b["building_id"],
            "name": b["name"],
            "level": b["level"],
            "workers": b["workers"],
            "max_workers": b["max_workers"],
            "efficiency": b["workers"] / max(b["max_workers"], 1),
            "produces": produces,
            "produces_name": item_name,
            "output": output,
            "requires": requires,
            "requires_name": input_name,
            "input_source": input_source,
            "is_in_chain": is_in_chain,
        })

    return report


def get_supply_chains(state: GameState) -> list[list[dict]]:
    """
    Get all unique production chains in the town.
    Each chain is a list of links from raw material to final product.
    """
    buildings_data = load_data("buildings.json")
    chains = []
    visited = set()

    # Start from buildings that don't require inputs (raw material producers)
    for b in state.buildings:
        bdata = buildings_data.get(b["building_id"], {})
        if bdata.get("requires") is None and bdata.get("produces"):
            chain = get_production_chain(b["building_id"], buildings_data)
            if len(chain) > 1:
                # Mark all buildings in this chain as visited
                for link in chain:
                    visited.add(link["building_id"])
                chains.append(chain)

    # Add standalone buildings (not in any chain)
    for b in state.buildings:
        if b["building_id"] not in visited:
            bdata = buildings_data.get(b["building_id"], {})
            if bdata.get("produces"):
                chains.append([{
                    "building_id": b["building_id"],
                    "name": bdata["name"],
                    "produces": bdata.get("produces"),
                    "requires": bdata.get("requires"),
                    "consumer_id": None,
                }])

    return chains


def format_production_messages(report: list[dict]) -> list[str]:
    """
    Format a production report into human-readable messages.
    Groups by supply chain for clarity.
    """
    messages = []

    # Group: buildings with workers vs idle
    active = [r for r in report if r["output"] > 0]
    idle = [r for r in report if r["output"] == 0]

    if active:
        messages.append("[bold]⚙️ Production Report:[/bold]")

        # Show chain info for buildings in chains
        chained = [r for r in active if r["is_in_chain"]]
        standalone = [r for r in active if not r["is_in_chain"]]

        if chained:
            messages.append("  [dim]Supply Chains:[/dim]")
            shown_chains = set()
            for r in chained:
                chain_key = (r["building_id"], r["produces"])
                if chain_key in shown_chains:
                    continue
                shown_chains.add(chain_key)

                # Build chain display
                chain_parts = [r["name"]]
                if r["requires_name"] and r["input_source"]:
                    chain_parts.insert(0, f"{r['input_source']} → {r['requires_name']}")
                chain_parts.append(f"→ {r['output']}x {r['produces_name']}")

                if r.get("requires_name"):
                    messages.append(
                        f"  {' → '.join(chain_parts)}"
                    )
                else:
                    messages.append(
                        f"  {r['name']}: +{r['output']}x {r['produces_name']}"
                    )

        if standalone:
            messages.append("  [dim]Standalone:[/dim]")
            for r in standalone:
                messages.append(
                    f"  {r['name']}: +{r['output']}x {r['produces_name']}"
                )

    if idle:
        idle_names = ", ".join(r["name"] for r in idle)
        messages.append(f"  [dim]Idle (no workers): {idle_names}[/dim]")

    return messages
