"""UI Utilities for GPT Rewind CLI"""

from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

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
            max_val = max(max_val, val)
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


def _get_date_range(sorted_dates):
    """Calculate the start and end dates for the heatmap."""
    end_date = datetime.strptime(sorted_dates[-1], "%Y-%m-%d").date()
    # Show last 52 weeks (approx 1 year)
    start_date = end_date - timedelta(weeks=51)

    # Adjust start_date to the preceding Sunday
    days_to_subtract = (start_date.weekday() + 1) % 7
    start_date = start_date - timedelta(days=days_to_subtract)

    # Adjust end_date to the following Saturday
    days_to_add = (6 - ((end_date.weekday() + 1) % 7)) % 7
    real_end_date = end_date + timedelta(days=days_to_add)

    return start_date, real_end_date


def _get_heatmap_cell_style(count, max_count):
    """Determine color and character for a heatmap cell."""
    if count == 0:
        return "bright_black", "■"

    ratio = count / max_count if max_count > 0 else 0

    if ratio <= 0.25:
        return "green4", "■"
    if ratio <= 0.5:
        return "green3", "■"
    if ratio <= 0.75:
        return "green1", "■"
    return "bright_green", "■"


def _build_heatmap_lines(start_date, real_end_date, date_map, max_count):
    """Build the grid lines for the heatmap."""
    lines = [[] for _ in range(7)]
    current = start_date
    while current <= real_end_date:
        date_str = current.strftime("%Y-%m-%d")
        count = date_map.get(date_str, 0)

        color, char = _get_heatmap_cell_style(count, max_count)

        # Sun=0, ..., Sat=6
        row_idx = (current.weekday() + 1) % 7
        lines[row_idx].append(f"[{color}]{char}[/{color}]")

        current += timedelta(days=1)

        # Safety break
        if (current - start_date).days > 400:
            break

    return lines


def _get_raw_month_labels(start_date, num_cols):
    """Identify columns where new months start."""
    month_labels = []

    # Always label the start month at col 0
    start_month_str = start_date.strftime("%b")
    month_labels.append((0, start_month_str))

    # Iterate through weeks to find months starts
    curr_week = start_date
    for col in range(num_cols):
        # Check if this week contains the 1st of any month
        for day_offset in range(7):
            day_check = curr_week + timedelta(days=day_offset)
            if day_check.day == 1:
                m_str = day_check.strftime("%b")
                # Avoid duplicate if it's the same as the start month at col 0
                if not (col == 0 and m_str == start_month_str):
                    month_labels.append((col, m_str))
                break

        curr_week += timedelta(days=7)
    return month_labels


def _generate_month_header(start_date, num_cols):
    """Generate the month header string."""
    month_labels = _get_raw_month_labels(start_date, num_cols)

    # Filter overlapping labels
    final_labels = []
    last_end_pos = -2  # Allow small buffer

    for col, txt in month_labels:
        # Each column visually takes 2 chars (char + space)
        pos = col * 2
        if pos > last_end_pos:
            final_labels.append((pos, txt))
            last_end_pos = pos + len(txt)

    # Construct header string
    header_chars = [" "] * (num_cols * 2)
    for pos, txt in final_labels:
        if pos + len(txt) <= len(header_chars):
            for i, char in enumerate(txt):
                header_chars[pos + i] = char

    return "".join(header_chars).rstrip()


def print_heatmap(data, title=None):
    """
    Prints a contribution graph (heatmap) similar to GitHub's.
    data: List of dicts with 'date' (YYYY-MM-DD) and 'counts' keys.
    """
    if not data:
        console.print("[yellow]No data available.[/yellow]")
        return

    console.print(f"\n[bold underline]{title}[/bold underline]")

    # Parse dates and counts
    date_map = {
        item.get("date"): item.get("counts", 0)
        for item in data
        if item.get("date")
    }

    if not date_map:
        return

    # Determine range
    sorted_dates = sorted(date_map.keys())
    start_date, real_end_date = _get_date_range(sorted_dates)

    # Determine max count for scaling
    max_count = max(date_map.values()) if date_map else 0

    # Build grid lines
    lines = _build_heatmap_lines(start_date, real_end_date, date_map, max_count)

    # Build Month Header
    num_cols = len(lines[0]) if lines else 0
    header_str = _generate_month_header(start_date, num_cols)

    # Print Header with padding for row labels (4 spaces)
    console.print(f"    {header_str}")

    # Print
    days_labels = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for i, line in enumerate(lines):
        label = f"{days_labels[i]:<3}" if i % 2 == 1 else "   "
        console.print(f"{label} {' '.join(line)}")

    # Legend
    console.print(
        "    [dim]Less[/dim] [bright_black]■[/bright_black] [green4]■[/green4] "
        "[green3]■[/green3] [green1]■[/green1] [bright_green]■[/bright_green] [dim]More[/dim]"
    )
