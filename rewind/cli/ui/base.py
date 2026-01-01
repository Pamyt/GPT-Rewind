"""
Base UI Utilities for GPT Rewind CLI
"""
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

# Shared console instance
console = Console()


def print_header(title, panel_style="bold magenta"):
    """
    Prints a centered header with a panel style.
    """
    console.print(
        Panel(
            Text(title, justify="center"),
            style=panel_style,
            expand=False,
            padding=(0, 2),
        )
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
