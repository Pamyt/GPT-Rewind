"""
Heatmap Utilities for GPT Rewind CLI
"""
from datetime import datetime, timedelta
from .base import console


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
