"""Supply chain — goods flow, bottleneck detection, chain health."""

from src.core.game_state import GameState
from src.core.logger import get_logger
from src.utils.data_loader import load_data
from src.systems.production import get_building_output

log = get_logger(__name__)


def analyze_supply_chain(state: GameState, weather_mod: float = 1.0) -> list[dict]:
    """
    Analyze the full supply chain for all buildings.
    Models actual goods flow: producer output → consumer input.
    Detects bottlenecks where producer can't meet consumer demand.
    Returns a list of chain analyses.
    """
    buildings_data = load_data("buildings.json")
    chains = []

    # Build a map of building outputs
    building_outputs = {}
    for b in state.buildings:
        bdata = buildings_data.get(b["building_id"], {})
        if bdata.get("produces") and b["workers"] > 0:
            output = get_building_output(b, weather_mod)
            building_outputs[b["building_id"]] = {
                "output": output,
                "produces": bdata["produces"],
                "workers": b["workers"],
                "max_workers": b["max_workers"],
            }

    # Trace each chain from raw material producers
    visited = set()
    for b in state.buildings:
        bdata = buildings_data.get(b["building_id"], {})
        if bdata.get("requires") is not None or not bdata.get("produces"):
            continue

        # Start of a chain — raw material producer
        chain = _trace_chain(b["building_id"], state, buildings_data, building_outputs, visited)
        if chain:
            chains.append(_analyze_chain(chain, state, building_outputs))

    # Add standalone buildings not in any chain
    for b in state.buildings:
        if b["building_id"] not in visited:
            bdata = buildings_data.get(b["building_id"], {})
            if bdata.get("produces"):
                output = building_outputs.get(b["building_id"], {}).get("output", 0)
                # Find market item name
                item_name = bdata["produces"].capitalize()
                for m in state.market:
                    if m["item_id"] == bdata["produces"]:
                        item_name = m["name"]
                        break

                chains.append({
                    "links": [{
                        "building_id": b["building_id"],
                        "name": b["name"],
                        "produces": bdata["produces"],
                        "produces_name": item_name,
                        "output": output,
                        "workers": b["workers"],
                        "max_workers": b["max_workers"],
                        "requires": None,
                        "input_need": 0,
                        "input_available": 0,
                        "status": _chain_status(output, 0, 0),
                    }],
                    "health": "healthy" if output > 0 else "idle",
                    "bottleneck": None,
                    "total_output": output,
                })

    return chains


def _trace_chain(
    start_id: str,
    state: GameState,
    buildings_data: dict,
    building_outputs: dict,
    visited: set,
) -> list[dict] | None:
    """Trace a supply chain from a raw material producer."""
    chain = []
    current_id = start_id

    while current_id:
        if current_id in visited:
            break
        visited.add(current_id)

        # Find this building in town
        building = None
        for b in state.buildings:
            if b["building_id"] == current_id:
                building = b
                break

        if building is None:
            break

        bdata = buildings_data.get(current_id, {})
        produces = bdata.get("produces")
        requires = bdata.get("requires")

        if not produces:
            break

        output = building_outputs.get(current_id, {}).get("output", 0)

        # Find market item name
        item_name = produces.capitalize()
        for m in state.market:
            if m["item_id"] == produces:
                item_name = m["name"]
                break

        chain.append({
            "building_id": current_id,
            "name": building["name"],
            "produces": produces,
            "produces_name": item_name,
            "output": output,
            "workers": building["workers"],
            "max_workers": building["max_workers"],
            "requires": requires,
        })

        # Find the consumer of this output
        consumer_id = None
        for bid, other in buildings_data.items():
            if other.get("requires") == produces and bid != current_id:
                # Check if consumer exists in town
                for b in state.buildings:
                    if b["building_id"] == bid:
                        consumer_id = bid
                        break
                break

        current_id = consumer_id

    return chain if chain else None


def _analyze_chain(
    chain: list[dict],
    state: GameState,
    building_outputs: dict,
) -> dict:
    """Analyze a supply chain for bottlenecks and health."""
    links = []
    bottleneck = None
    total_output = 0

    for i, link in enumerate(chain):
        requires = link["requires"]
        input_available = 0
        input_need = 0

        if requires and i > 0:
            # Input comes from previous link's output
            prev_link = chain[i - 1]
            input_available = building_outputs.get(prev_link["building_id"], {}).get("output", 0)
            # Consumer needs roughly what it can process
            input_need = link["output"] if link["output"] > 0 else 0

        status = _chain_status(link["output"], input_need, input_available)

        if status in ("broken", "strained") and bottleneck is None:
            bottleneck = link["name"]

        if i == len(chain) - 1:
            total_output = link["output"]

        links.append({
            **link,
            "input_need": input_need,
            "input_available": input_available,
            "status": status,
        })

    # Determine overall chain health
    statuses = [l["status"] for l in links]
    if "broken" in statuses:
        health = "broken"
    elif "strained" in statuses:
        health = "strained"
    elif all(s == "healthy" for s in statuses):
        health = "healthy"
    elif all(s == "idle" for s in statuses):
        health = "idle"
    else:
        health = "mixed"

    return {
        "links": links,
        "health": health,
        "bottleneck": bottleneck,
        "total_output": total_output,
    }


def _chain_status(output: int, input_need: int, input_available: int) -> str:
    """Determine the status of a single chain link."""
    if output == 0:
        return "idle"
    if input_need > 0 and input_available < input_need * 0.5:
        return "broken"
    if input_need > 0 and input_available < input_need:
        return "strained"
    return "healthy"


def process_goods_flow(state: GameState, weather_mod: float) -> list[str]:
    """
    Process the actual flow of goods through supply chains.
    Producer output goes to a virtual warehouse, consumers pull from it.
    Returns messages about chain disruptions.
    """
    buildings_data = load_data("buildings.json")
    messages = []

    # Step 1: All producers create goods
    production_map = {}  # item_id -> total produced
    for b in state.buildings:
        bdata = buildings_data.get(b["building_id"], {})
        produces = bdata.get("produces")
        if not produces or b["workers"] <= 0:
            continue

        from src.systems.workforce import get_worker_modifier
        worker_mod = get_worker_modifier(state, b["building_id"])
        worker_ratio = b["workers"] / max(b["max_workers"], 1)
        output = int(10 * worker_ratio * weather_mod * b["level"] * worker_mod)

        production_map[produces] = production_map.get(produces, 0) + output

        # Add to market supply
        for item in state.market:
            if item["item_id"] == produces:
                item["supply"] += output
                break

    # Step 2: All consumers pull goods from their input source
    for b in state.buildings:
        bdata = buildings_data.get(b["building_id"], {})
        requires = bdata.get("requires")
        if not requires or b["workers"] <= 0:
            continue

        # Find how much of the input was produced locally
        local_production = production_map.get(requires, 0)

        # Calculate how much this building needs
        from src.systems.workforce import get_worker_modifier
        worker_mod = get_worker_modifier(state, b["building_id"])
        worker_ratio = b["workers"] / max(b["max_workers"], 1)
        needed = int(10 * worker_ratio * weather_mod * b["level"] * worker_mod)

        # Consume from market (which includes local production)
        for item in state.market:
            if item["item_id"] == requires:
                consumed = min(needed, item["supply"])
                item["supply"] = max(0, item["supply"] - consumed)

                # Report shortages
                if consumed < needed * 0.5:
                    messages.append(
                        f"  [red]⚠ {b['name']} shortage: needed {needed} {item['name']}, "
                        f"only got {consumed}![/red]"
                    )
                break

    return messages


def get_chain_summary(state: GameState, weather_mod: float = 1.0) -> dict:
    """Get a summary of all supply chains."""
    chains = analyze_supply_chain(state, weather_mod)

    total_chains = len(chains)
    healthy = sum(1 for c in chains if c["health"] == "healthy")
    strained = sum(1 for c in chains if c["health"] == "strained")
    broken = sum(1 for c in chains if c["health"] == "broken")
    idle = sum(1 for c in chains if c["health"] == "idle")
    bottlenecks = [c["bottleneck"] for c in chains if c["bottleneck"]]

    return {
        "total_chains": total_chains,
        "healthy": healthy,
        "strained": strained,
        "broken": broken,
        "idle": idle,
        "bottlenecks": bottlenecks,
    }
