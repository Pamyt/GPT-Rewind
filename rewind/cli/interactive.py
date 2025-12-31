"""Interactive Mode for GPT Rewind CLI"""
import glob
import questionary
from rewind.cli.ui import console, print_header
from rewind.cli.handlers import handle_overview, handle_style, handle_time


def scan_json_files():
    """Scan for JSON files in data/ and root directory."""
    files = glob.glob("data/*.json")
    # Also look in root for convenience if data folder is empty or not found
    files.extend(glob.glob("*.json"))
    if not files:
        # Fallback to a known example if nothing found, though this might fail later
        return ["data/example_deepseek.json"]
    return sorted(files)


def interactive_mode():
    """Run the interactive mode of the CLI."""
    console.clear()
    print_header("GPT Rewind CLI", panel_style="bold white on blue")
    console.print("[dim]Use arrow keys to navigate and Enter to select[/dim]\n")

    # 1. Select File
    json_files = scan_json_files()
    if not json_files:
        console.print(
            "[bold red]No JSON files found in data/ or root directory![/bold red]"
        )
        return

    file_path = questionary.select("Select data file:", choices=json_files).ask()

    if not file_path:
        return

    # 2. Select Provider
    provider = questionary.select(
        "Select provider type:",
        choices=["deepseek", "openai", "claude", "qwen"],
        default="deepseek",
    ).ask()

    if not provider:
        return

    while True:
        console.rule()
        action = questionary.select(
            "What would you like to see?",
            choices=[
                "Overview (Session, Models, Language)",
                "Style (Emoji, Politeness)",
                "Time (Frequency, Distribution)",
                "Change File/Provider",
                "Exit",
            ],
        ).ask()

        if action == "Exit" or action is None:
            console.print("[bold green]Goodbye![/bold green]")
            break

        if action == "Change File/Provider":
            file_path = questionary.select(
                "Select data file:", choices=scan_json_files()
            ).ask()
            if not file_path:
                break
            provider = questionary.select(
                "Select provider type:",
                choices=["deepseek", "openai", "claude", "qwen"],
            ).ask()
            if not provider:
                break
            continue

        console.print("\n")
        if action.startswith("Overview"):
            handle_overview(file_path, provider)

        elif action.startswith("Style"):
            handle_style(file_path, provider)

        elif action.startswith("Time"):
            handle_time(file_path, provider)

        console.print("\n")
        questionary.press_any_key_to_continue().ask()
