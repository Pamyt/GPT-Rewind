"""Handler for rewind cli"""
import json
from rewind.apis import base_api, style_api, time_api
from rewind.utils.providers import ProviderType
from rewind.cli.ui import (
    console,
    print_header,
    print_table,
    print_simple_dict,
    print_bar_chart,
    print_distribution_bar,
    print_heatmap,
    print_emoji_rect,
)


def get_provider_enum(provider_str):
    """Convert string provider to ProviderType enum"""
    return ProviderType(provider_str.lower())


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
        print_emoji_rect(style_api.emoji_counts(file, provider_type), title="Emoji Wall")

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


def _print_daily_heatmap(file, provider_type):
    days = time_api.chat_days(file, provider_type)
    if days:
        print_heatmap(days, title="Daily Activity Heatmap")
    else:
        console.print("\n[bold underline]Daily Activity Heatmap[/bold underline]")
        console.print("[yellow]No data available.[/yellow]")


def _print_time_limits(file, provider_type):
    print_header("Time Limits")
    limits = time_api.time_limit(file, provider_type)
    flat_limits = {}
    for item in limits:
        flat_limits.update(item)
    print_simple_dict(flat_limits)


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
        _print_daily_heatmap(file, provider_type)
        _print_time_limits(file, provider_type)
        _print_hourly_distribution(file, provider_type)

    except (OSError, json.JSONDecodeError, AttributeError) as error:
        console.print(f"[bold red]Error:[/bold red] {error}")
