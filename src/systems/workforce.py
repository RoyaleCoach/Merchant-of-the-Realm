"""Workforce management — payroll, worker stats, skill-based production."""

from src.core.game_state import GameState
from src.core.logger import get_logger

log = get_logger(__name__)


def get_workers_at_building(state: GameState, building_id: str) -> list[dict]:
    """Get all NPCs working at a specific building."""
    return [n for n in state.npcs if n.get("workplace") == building_id]


def get_total_workers(state: GameState) -> int:
    """Get total number of employed workers."""
    return sum(1 for n in state.npcs if n.get("workplace") is not None)


def get_total_payroll(state: GameState) -> int:
    """Calculate total daily wage cost for all workers."""
    return sum(
        n.get("salary", 10)
        for n in state.npcs
        if n.get("workplace") is not None
    )


def get_building_worker_count(state: GameState, building_id: str) -> int:
    """Get number of workers at a building."""
    return sum(1 for n in state.npcs if n.get("workplace") == building_id)


def get_average_skill(state: GameState, building_id: str) -> float:
    """Get average skill level of workers at a building."""
    workers = get_workers_at_building(state, building_id)
    if not workers:
        return 0.0
    return sum(w.get("skill", 1) for w in workers) / len(workers)


def get_worker_modifier(state: GameState, building_id: str) -> float:
    """
    Calculate the worker productivity modifier for a building.
    Based on: average skill, average morale, average health.
    Returns a multiplier (0.5 to 2.0).
    """
    workers = get_workers_at_building(state, building_id)
    if not workers:
        return 0.0

    avg_skill = sum(w.get("skill", 1) for w in workers) / len(workers)
    avg_morale = sum(w.get("morale", 50) for w in workers) / len(workers)
    avg_health = sum(w.get("health", 100) for w in workers) / len(workers)

    # Skill contributes 50%, morale 30%, health 20%
    skill_factor = avg_skill / 5.0  # normalize: skill 5 = 1.0
    morale_factor = avg_morale / 100.0
    health_factor = avg_health / 100.0

    modifier = (skill_factor * 0.5) + (morale_factor * 0.3) + (health_factor * 0.2)
    return max(0.1, min(2.0, modifier))


def pay_workers(state: GameState) -> tuple[int, str]:
    """
    Pay all workers their daily wages.
    Returns (amount_paid, message).
    If not enough gold, workers get unhappy.
    """
    total_payroll = get_total_payroll(state)
    workers = [n for n in state.npcs if n.get("workplace") is not None]

    if not workers:
        return 0, "No workers to pay."

    if state.gold >= total_payroll:
        state.gold -= total_payroll
        # Workers are happy when paid
        for w in workers:
            w["morale"] = min(100, w.get("morale", 50) + 2)
            w["experience"] = w.get("experience", 0) + 1
            # Skill improves with experience
            if w["experience"] > 10 and w.get("skill", 1) < 10:
                w["skill"] = min(10, w.get("skill", 1) + 1)
                w["experience"] = 0  # reset for next level
                log.info(f"{w['name']} skill increased to {w['skill']}")

        log.info(f"Paid {total_payroll}g to {len(workers)} workers")
        return total_payroll, f"Paid {total_payroll}g to {len(workers)} workers."
    else:
        # Can't pay — workers get angry
        for w in workers:
            w["morale"] = max(0, w.get("morale", 50) - 15)
            w["loyalty"] = max(0, w.get("loyalty", 50) - 10)

        log.warning(f"Could not pay workers! Need {total_payroll}g, have {state.gold}g")
        return 0, f"[red]Not enough gold! Need {total_payroll}g, have {state.gold}g. Workers are angry![/red]"


def update_worker_stats(state: GameState) -> None:
    """Daily update for worker stats (morale, health, experience)."""
    for npc in state.npcs:
        if not npc.get("workplace"):
            continue

        # Morale slowly drifts toward neutral (50)
        morale = npc.get("morale", 50)
        if morale > 50:
            npc["morale"] = max(50, morale - 1)
        elif morale < 50:
            npc["morale"] = min(50, morale + 1)

        # Health slowly regenerates if not at max
        if npc.get("health", 100) < 100:
            npc["health"] = min(100, npc.get("health", 100) + 1)

        # Small chance of health event
        import random
        if random.random() < 0.02:  # 2% chance
            npc["health"] = max(0, npc.get("health", 100) - random.randint(5, 15))


def get_workforce_summary(state: GameState) -> dict:
    """Get a summary of the entire workforce."""
    workers = [n for n in state.npcs if n.get("workplace") is not None]

    if not workers:
        return {
            "total_workers": 0,
            "total_payroll": 0,
            "avg_skill": 0,
            "avg_morale": 0,
            "avg_health": 0,
            "buildings_staffed": 0,
        }

    return {
        "total_workers": len(workers),
        "total_payroll": get_total_payroll(state),
        "avg_skill": sum(w.get("skill", 1) for w in workers) / len(workers),
        "avg_morale": sum(w.get("morale", 50) for w in workers) / len(workers),
        "avg_health": sum(w.get("health", 100) for w in workers) / len(workers),
        "buildings_staffed": len(set(w["workplace"] for w in workers)),
    }
