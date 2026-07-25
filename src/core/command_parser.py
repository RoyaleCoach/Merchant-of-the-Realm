"""Command parser — converts text input into structured commands."""

from dataclasses import dataclass


@dataclass
class Command:
    """A parsed player command."""
    action: str
    args: list[str]
    raw: str


def parse(input_str: str) -> Command:
    """
    Parse raw player input into a Command.

    Examples:
        "next"         → Command(action="next", args=[], raw="next")
        "buy bread 20" → Command(action="buy", args=["bread", "20"], raw="buy bread 20")
        "save my_game" → Command(action="save", args=["my_game"], raw="save my_game")
    """
    raw = input_str.strip()
    if not raw:
        return Command(action="empty", args=[], raw=raw)

    parts = raw.lower().split()
    action = parts[0]
    args = parts[1:]

    return Command(action=action, args=args, raw=raw)
