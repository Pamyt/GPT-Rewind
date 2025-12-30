"""Rewind CLI Tool"""

import sys
import os
import glob
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
import questionary
from rewind.apis import base_api, style_api, time_api
from rewind.utils.providers import ProviderType

# Ensure the current directory is in the python path to import rewind modules
sys.path.append(os.getcwd())

console = Console()


def get_provider_enum(provider_str):
    """Convert string provider to ProviderType enum"""
    return ProviderType(provider_str.lower())


def print_header(title, panel_style="bold magenta"):
    """
    Prints a centered header with a panel style.
    """
    console.print(
        Panel(Text(title, justify="center"), style=panel_style, expand=False, padding=(0, 2))
    )


def print_table(data, title=None):
    """
    Prints a table for list or dict data, with optional title.
    Handles complex nested structures like dictionaries with 'title' and 'id' keys.
    """
    if not data:
        console.print("[yellow]No data available.[/yellow]")
        return

    # Pre-process data
    clean_data = []
    if isinstance(data, list):
        clean_data = data
    elif isinstance(data, dict):
        clean_data = [{"Key": k, "Value": v} for k, v in data.items()]

    if not clean_data:
        console.print("[yellow]No data available.[/yellow]")
        return

    # Create table
    table = Table(
        title=title, box=box.ROUNDED, show_header=True, header_style="bold cyan"
    )

    # Add columns based on first item keys
    keys = list(clean_data[0].keys())
    for key in keys:
        table.add_column(str(key).replace("_", " ").title())

    # Add rows
    for item in clean_data:
        row = []
        for k in keys:
            val = item.get(k, "")
            # Handle complex objects
            if isinstance(val, dict) and ("title" in val or "id" in val):
                title_s = val.get("title", "No Title")
                sid = val.get("id", "No ID")
                row.append(f"{title_s}\n(ID: {sid})")
            elif isinstance(val, dict):
                row.append(str(val)[:50] + "...")
            else:
                row.append(str(val))
        table.add_row(*row)

    console.print(table)


def print_simple_dict(data, title=None):
    """
    Prints a simple key-value table for dictionary data,
    with optional title.
    """
    if not data:
        console.print("[yellow]No data available.[/yellow]")
        return

    table = Table(title=title, box=box.SIMPLE, show_header=False)
    table.add_column("Key", style="bold green")
    table.add_column("Value", style="white")

    for key, value in data.items():
        table.add_row(str(key).replace("_", " ").title(), str(value))

    console.print(table)


def print_bar_chart(data, title=None, label_key="key", value_key="value"):
    """
    Prints a horizontal bar chart to represent key-value pairs,
    with optional title and custom label/value keys.
    """
    if not data:
        return

    console.print(f"\n[bold underline]{title}[/bold underline]")

    # Find max value for scaling
    max_val = 0
    for item in data:
        try:
            val = float(item.get(value_key, 0))
            if val > max_val:
                max_val = val
        except (ValueError, TypeError):
            pass

    if max_val == 0:
        max_val = 1

    for item in data:
        label = str(item.get(label_key, ""))
        value = item.get(value_key, 0)
        try:
            num_val = float(value)
        except (ValueError, TypeError):
            num_val = 0

        bar_len = int((num_val / max_val) * 40)
        bar_str = "█" * bar_len
        # Different colors for different lengths/values could be added here
        color = "cyan" if num_val > 0 else "dim white"
        # Adjust label width to 7 to accommodate YYYY-MM
        console.print(f"{label:>7} | [{color}]{bar_str}[/{color}] {value}")


# --- Handler Functions ---


def _print_legend(items):
    """Prints the legend for the distribution bar."""
    # Create a table for the legend to keep it organized
    legend_table = Table(box=None, show_header=False, padding=(0, 2))
    legend_table.add_column("Legend 1")
    legend_table.add_column("Legend 2")

    # Group items into pairs for two-column layout
    current_row = []

    for item in items:
        val = item["value"]
        val_display = int(val) if val.is_integer() else val
        pct_str = f"{item['pct']*100:.1f}%"
        legend_item = f"[{item['color']}]■[/{item['color']}] {item['label']}:\
            [bold]{val_display}[/bold] ({pct_str})"
        current_row.append(legend_item)

        if len(current_row) == 2:
            legend_table.add_row(*current_row)
            current_row = []

    if current_row:
        legend_table.add_row(*current_row)

    console.print(legend_table)
    console.print()


def print_distribution_bar(data, title=None, label_key="key", value_key="value"):
    """
    Prints a horizontal stacked bar chart (similar to GitHub language bar)
    to represent distribution, serving as a CLI-friendly 'pie chart'.
    """
    if not data:
        return

    console.print(f"\n[bold underline]{title}[/bold underline]")

    # 1. Process Data & Calculate Percentages
    total = sum(float(item.get(value_key, 0)) for item in data)
    if total == 0:
        return

    # Filter out zero items and sort
    items = []
    for item in data:
        val = float(item.get(value_key, 0))
        if val > 0:
            items.append(
                {
                    "label": str(item.get(label_key, "")),
                    "value": val,
                    "pct": val / total,
                }
            )

    if not items:
        return

    # Sort by value desc
    items.sort(key=lambda x: x["value"], reverse=True)

    # 2. Assign Colors
    # Rich standard colors list
    colors = [
        "bright_cyan",
        "bright_green",
        "bright_yellow",
        "bright_magenta",
        "bright_blue",
        "bright_red",
        "white",
        "cyan",
        "green",
        "yellow",
        "magenta",
        "blue",
        "red",
        "red",
    ]

    # 3. Build the Bar
    bar_width = 60  # Total characters for the bar
    bar_segments = []

    remaining_len = bar_width

    for i, item in enumerate(items):
        color = colors[i % len(colors)]
        item["color"] = color

        # Calculate segment length
        # For the last item, take the remaining space to ensure full width (if it's significant)
        if i == len(items) - 1:
            seg_len = remaining_len
        else:
            seg_len = int(item["pct"] * bar_width)

        if seg_len > 0:
            bar_segments.append(f"[{color}]{'█' * seg_len}[/{color}]")
            remaining_len -= seg_len
        else:
            # If segment is too small to show a char, we might skip it in the bar but show in legend
            pass

    console.print("".join(bar_segments))
    console.print()

    # 4. Print Legend (Grid layout)
    _print_legend(items)


def _print_model_usage(file, provider_type):
    print_header("Most Used Models")
    models = base_api.most_used_models(file, provider_type)
    if models:
        try:
            models.sort(key=lambda x: x["usage"], reverse=True)
        except (ValueError, TypeError):
            pass
        print_distribution_bar(
            models,
            title="Model Usage Distribution",
            label_key="model",
            value_key="usage",
        )
    else:
        console.print("[yellow]No data available.[/yellow]")


def _print_character_counts(file, provider_type):
    print_header("Total Characters")
    chars = base_api.total_characters(file, provider_type)
    if chars:
        try:
            chars.sort(key=lambda x: x["counts"], reverse=True)
        except (ValueError, TypeError):
            pass
        for item in chars:
            item["label"] = item["model_type"].replace("_", " ").title()
        print_distribution_bar(
            chars,
            title="Character Counts by Model/Type",
            label_key="label",
            value_key="counts",
        )
    else:
        console.print("[yellow]No data available.[/yellow]")


def _print_language_stats(file, provider_type):
    print_header("Most Used Language")
    langs = base_api.most_used_language(file, provider_type)
    if not langs:
        console.print("[yellow]No data available.[/yellow]")
        return

    natural_summary = {}
    code_summary = {}

    for item in langs:
        lang = item.get("language", "unknown")
        count = item.get("counts", 0)
        l_type = item.get("type", "natural")

        if l_type == "natural":
            natural_summary[lang] = natural_summary.get(lang, 0) + count
        elif l_type == "code":
            code_summary[lang] = code_summary.get(lang, 0) + count

    if natural_summary:
        nat_list = [{"language": k, "count": v} for k, v in natural_summary.items()]
        nat_list.sort(key=lambda x: x["count"], reverse=True)
        print_distribution_bar(
            nat_list,
            title="Natural Language Distribution",
            label_key="language",
            value_key="count",
        )

    if code_summary:
        code_list = [{"language": k, "count": v} for k, v in code_summary.items()]
        code_list.sort(key=lambda x: x["count"], reverse=True)
        print_distribution_bar(
            code_list,
            title="Code Language Distribution",
            label_key="language",
            value_key="count",
        )

    if not natural_summary and not code_summary:
        console.print("[yellow]No data available.[/yellow]")


def handle_overview(file, provider):
    """Handle overview analysis for the given file and provider."""
    provider_type = get_provider_enum(provider)
    try:
        print_header("Session Count Stats")
        print_simple_dict(base_api.session_count(file, provider_type))

        _print_model_usage(file, provider_type)
        _print_character_counts(file, provider_type)
        _print_language_stats(file, provider_type)

        print_header("Refuse Counts")
        console.print(
            f"[bold red]Refusals:[/bold red] {base_api.refuse_counts(file, provider_type)}"
        )

    except (OSError, json.JSONDecodeError, AttributeError) as error:
        console.print(f"[bold red]Error:[/bold red] {error}")


def handle_style(file, provider):
    """Handle style analysis for the given file and provider."""
    provider_type = get_provider_enum(provider)
    try:
        print_header("Emoji Counts")
        print_table(style_api.emoji_counts(file, provider_type))

        print_header("Politeness Extent")
        print_table(style_api.polite_extent(file, provider_type))

    except (OSError, json.JSONDecodeError, AttributeError) as error:
        console.print(f"[bold red]Error:[/bold red] {error}")


def _print_monthly_frequency(file, provider_type):
    # Removed "Chat Frequency by Day" as requested
    months = time_api.chat_months(file, provider_type)
    if months:
        try:
            months.sort(key=lambda x: x["date"])
        except (ValueError, TypeError):
            pass
        print_bar_chart(
            months,
            title="Chat Frequency by Month",
            label_key="date",
            value_key="counts",
        )
    else:
        console.print("\n[bold underline]Chat Frequency by Month[/bold underline]")
        console.print("[yellow]No data available.[/yellow]")


def _print_time_limits(file, provider_type):
    print_header("Time Limits")
    limits = time_api.time_limit(file, provider_type)
    flat_limits = {}
    for item in limits:
        flat_limits.update(item)

    table = Table(box=box.SIMPLE, show_header=False)
    table.add_column("Key", style="bold green")
    table.add_column("Value", style="white")
    for key, value in flat_limits.items():
        if isinstance(value, dict) and ("title" in value or "id" in value):
            title_s = value.get("title", "No Title")
            sid = value.get("id", "No ID")
            val_str = f"{title_s} (ID: {sid})"
        else:
            val_str = str(value)
        table.add_row(str(key).replace("_", " ").title(), val_str)
    console.print(table)


def _print_hourly_distribution(file, provider_type):
    print_header("Per Hour Distribution")
    dist = time_api.per_hour_distribution(file, provider_type)
    if dist:
        formatted_dist = [{"hour": int(k), "count": v} for k, v in dist.items()]
        formatted_dist.sort(key=lambda x: x["hour"])
        print_bar_chart(
            formatted_dist,
            title="Activity per Hour (0-23)",
            label_key="hour",
            value_key="count",
        )
    else:
        console.print("No data available.")


def handle_time(file, provider):
    """Handle time analysis for the given file and provider."""
    provider_type = get_provider_enum(provider)
    try:
        _print_monthly_frequency(file, provider_type)
        _print_time_limits(file, provider_type)
        _print_hourly_distribution(file, provider_type)

    except (OSError, json.JSONDecodeError, AttributeError) as error:
        console.print(f"[bold red]Error:[/bold red] {error}")


# --- Interactive Mode ---


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


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """GPT Rewind CLI Tool to inspect API data"""
    if ctx.invoked_subcommand is None:
        interactive_mode()


@cli.command()
@click.option("--file", "-f", required=True, help="Path to the JSON data file")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "deepseek", "claude", "qwen"], case_sensitive=False),
    default="deepseek",
    help="Provider type",
)
def overview(file, provider):
    """Show basic data overview"""
    handle_overview(file, provider)


@cli.command()
@click.option("--file", "-f", required=True, help="Path to the JSON data file")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "deepseek", "claude", "qwen"], case_sensitive=False),
    default="deepseek",
    help="Provider type",
)
def style(file, provider):
    """Show style analysis"""
    handle_style(file, provider)


@cli.command()
@click.option("--file", "-f", required=True, help="Path to the JSON data file")
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "deepseek", "claude", "qwen"], case_sensitive=False),
    default="deepseek",
    help="Provider type",
)
def time(file, provider):
    """Show time analysis"""
    handle_time(file, provider)


if __name__ == "__main__":
    cli()  # pylint: disable=no-value-for-parameter
