"""Medieval Market Tycoon — Entry point."""

from src.core.game_loop import create_new_game, run_game_loop
from src.core.save_manager import list_saves
from src.ui.renderer import show_banner, show_main_menu, show_save_list, show_goodbye, console


def main():
    """Main entry point with menu loop."""
    show_banner()

    while True:
        show_main_menu()
        console.print()
        choice = console.input("[cyan]Choose an option: [/cyan]").strip()

        match choice:
            case "1":
                state = create_new_game()
                run_game_loop(state)

            case "2":
                saves = list_saves()
                show_save_list(saves)
                if saves:
                    slot = console.input("\n[cyan]Slot to load (or Enter to cancel): [/cyan]").strip()
                    if slot:
                        from src.core.game_state import GameState
                        from src.core.save_manager import load_game
                        data = load_game(slot)
                        if data:
                            state = GameState.from_dict(data)
                            console.print(f"[green]Loaded '{slot}'.[/green]")
                            run_game_loop(state)
                        else:
                            console.print(f"[red]Save '{slot}' not found.[/red]")

            case "3":
                show_goodbye()
                break

            case "":
                continue

            case _:
                console.print("[red]Invalid option. Choose 1, 2, or 3.[/red]")

        console.print()


if __name__ == "__main__":
    main()
