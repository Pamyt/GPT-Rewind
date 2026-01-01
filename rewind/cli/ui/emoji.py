"""
Emoji Visualization Utilities for GPT Rewind CLI
"""
import math
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.columns import Columns
from .base import console, print_header


def print_emoji_wall(data, title=None):
    """
    Prints an emoji wall similar to GitHub's language bar,
    with color-coded tiles based on emoji count.
    """
    if not data:
        console.print("[yellow]No data available.[/yellow]")
        return

    if title:
        print_header(title)

    items = []
    for item in data:
        emo = str(item.get("emoji", ""))
        raw = item.get("counts", 0)
        try:
            cnt = int(raw)
        except (ValueError, TypeError):
            cnt = 0
        if emo:
            items.append({"emoji": emo, "counts": cnt})

    if not items:
        console.print("[yellow]No data available.[/yellow]")
        return

    items.sort(key=lambda x: x["counts"], reverse=True)
    max_count = items[0]["counts"] if items else 1
    if max_count == 0:
        max_count = 1

    def bg_style(count_val):
        ratio = count_val / max_count
        if ratio <= 0.2:
            return "on grey23"
        if ratio <= 0.4:
            return "on grey35"
        if ratio <= 0.6:
            return "on blue3"
        if ratio <= 0.8:
            return "on blue"
        return "on bright_blue"

    tiles = []
    for item in items:
        style = bg_style(item["counts"])
        tiles.append(
            Panel(
                Text(item["emoji"], justify="center"),
                subtitle=str(item["counts"]),
                subtitle_align="right",
                box=box.ROUNDED,
                padding=(0, 1),
                width=8,
                style=style,
            )
        )

    console.print(Columns(tiles, equal=True, expand=True))


def print_emoji_mosaic(data, title=None):
    """
    Prints an emoji mosaic similar to GitHub's language bar,
    with color-coded tiles based on emoji count.
    """
    if not data:
        console.print("[yellow]No data available.[/yellow]")
        return

    if title:
        print_header(title)

    items = []
    for item in data:
        emo = str(item.get("emoji", ""))
        raw = item.get("counts", 0)
        try:
            cnt = int(raw)
        except (ValueError, TypeError):
            cnt = 0
        if emo and cnt > 0:
            items.append({"emoji": emo, "counts": cnt})

    if not items:
        console.print("[yellow]No data available.[/yellow]")
        return

    items.sort(key=lambda x: x["counts"], reverse=True)
    top = items[:12]
    total = sum(i["counts"] for i in top)
    if total == 0:
        console.print("[yellow]No data available.[/yellow]")
        return

    capacity = max(60, min(480, console.size.width * 6))
    alloc = []
    rem = capacity
    for i, item in enumerate(top):
        if i == len(top) - 1:
            count = max(1, rem)
        else:
            count = max(1, round(item["counts"] / total * capacity))
            rem -= count
        alloc.append((item["emoji"], count))

    tiles = []
    for emo, count in alloc:
        for _ in range(count):
            tiles.append(
                Panel(
                    Text(emo, justify="center"),
                    box=box.SIMPLE,
                    padding=(0, 0),
                    width=4,
                )
            )

    console.print(Columns(tiles, equal=True, expand=True))


def _find_best_split(sub_items, total_w, axis_len):
    """
    Finds the best index to split sub_items into two groups
    to match the spatial aspect ratio.
    Returns (best_k, best_split_pos).
    """
    best_k = 1
    best_split_pos = 1
    min_err = float('inf')

    current_w = 0
    # Optimization: We don't need to iterate all split_pos.
    # We can calculate target split_pos for each k.
    for k in range(1, len(sub_items)):
        current_w += sub_items[k - 1]["counts"]

        # Ideal ratio
        ratio = current_w / total_w

        # Ideal split pos
        target_pos = int(round(axis_len * ratio))
        target_pos = max(1, min(axis_len - 1, target_pos))

        # Calculate error
        area_ratio = target_pos / axis_len
        err = abs(area_ratio - ratio)

        if err < min_err:
            min_err = err
            best_k = k
            best_split_pos = target_pos

    return best_k, best_split_pos


def _fill_rect(grid, rect, char):
    """Fills a rectangle in the grid with a character."""
    x_pos, y_pos, width, height = rect
    grid_h = len(grid)
    grid_w = len(grid[0]) if grid_h > 0 else 0
    for row in range(y_pos, y_pos + height):
        for col in range(x_pos, x_pos + width):
            if row < grid_h and col < grid_w:
                grid[row][col] = char


def _recursive_layout(rect, sub_items, grid):
    """
    Recursively split the rectangle to fit items.
    rect is (x_pos, y_pos, width, height).
    """
    x_pos, y_pos, width, height = rect
    if not sub_items:
        return

    # Base case: only 1 item type, fill rect
    if len(sub_items) == 1:
        _fill_rect(grid, rect, sub_items[0]["emoji"])
        return

    # Split logic
    total_w = sum(i["counts"] for i in sub_items)
    if total_w == 0:
        return

    # Decide cut axis: cut the longer side
    # Simple aspect logic: width >= 2 * height => cut width (vertical split)
    if width >= 2 * height and width > 1:
        # Cut Width (Vertical line)
        axis_len = width
        split_vertical = True
    else:
        # Cut Height (Horizontal line)
        axis_len = height
        split_vertical = False

    if axis_len < 2:
        # Cannot split anymore spatially, give to the biggest one
        _recursive_layout(rect, [sub_items[0]], grid)
        return

    best_k, best_split_pos = _find_best_split(sub_items, total_w, axis_len)

    # Perform Split
    group_a = sub_items[:best_k]
    group_b = sub_items[best_k:]

    if split_vertical:
        # Left Rect: x, y, best_split_pos, h
        _recursive_layout(
            (x_pos, y_pos, best_split_pos, height), group_a, grid
        )
        # Right Rect: x+pos, y, w-pos, h
        _recursive_layout(
            (x_pos + best_split_pos, y_pos, width - best_split_pos, height),
            group_b, grid
        )
    else:
        # Top Rect: x, y, w, best_split_pos
        _recursive_layout(
            (x_pos, y_pos, width, best_split_pos), group_a, grid
        )
        # Bottom Rect: x, y+pos, w, h-pos
        _recursive_layout(
            (x_pos, y_pos + best_split_pos, width, height - best_split_pos),
            group_b, grid
        )


def _prepare_emoji_items(data):
    """Parses and filters data into emoji items."""
    items = []
    for item in data:
        emo = str(item.get("emoji", ""))
        raw = item.get("counts", 0)
        try:
            cnt = int(raw)
        except (ValueError, TypeError):
            cnt = 0
        if emo and cnt > 0:
            items.append({"emoji": emo, "counts": cnt})
    items.sort(key=lambda x: x["counts"], reverse=True)
    return items


def _calculate_scaled_items(items):
    """Scales item counts to fit a target total size."""
    num_types = len(items)
    # Target size:
    # We want a visually pleasing rectangle.
    # Base size ~800, max ~1200.
    target_total = max(400, num_types * 2)
    target_total = min(target_total, 1200)
    target_total = max(target_total, num_types)

    real_total = sum(i["counts"] for i in items)
    if real_total == 0:
        real_total = 1

    scale = target_total / real_total

    # Apply scale with min 1 constraint
    scaled_items = []
    current_scaled_sum = 0
    for item in items:
        s_cnt = max(1, round(item["counts"] * scale))
        scaled_items.append({"emoji": item["emoji"], "counts": s_cnt})
        current_scaled_sum += s_cnt

    return scaled_items, current_scaled_sum


def _adjust_items_to_rect(scaled_items, total_slots):
    """Adjusts scaled items to exactly fit the rectangle area."""
    width = min(60, max(30, console.size.width - 4))
    height = math.ceil(total_slots / width)

    # Re-adjust total slots to fill rectangle
    rect_area = width * height
    diff = rect_area - total_slots

    # Distribute diff to top items
    while diff != 0:
        if diff > 0:
            for item in scaled_items:
                item["counts"] += 1
                diff -= 1
                if diff == 0:
                    break
        else:
            for item in scaled_items:
                if item["counts"] > 1:
                    item["counts"] -= 1
                    diff += 1
                    if diff == 0:
                        break
    return width, height


def print_emoji_rect(data, title=None):
    """
    Prints a treemap-like emoji rectangle.
    """
    if not data:
        console.print("[yellow]No data available.[/yellow]")
        return

    if title:
        print_header(title)

    items = _prepare_emoji_items(data)
    if not items:
        console.print("[yellow]No data available.[/yellow]")
        return

    scaled_items, total_slots = _calculate_scaled_items(items)
    width, height = _adjust_items_to_rect(scaled_items, total_slots)

    # Grid: 2D array
    grid = [[" " for _ in range(width)] for _ in range(height)]

    # Execute Layout
    _recursive_layout((0, 0, width, height), scaled_items, grid)

    # Construct Wall
    for row in grid:
        console.print("".join(row))
