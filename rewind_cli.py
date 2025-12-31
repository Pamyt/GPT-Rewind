"""Rewind CLI Tool"""

import sys
import os
import click
from rewind.cli.handlers import handle_overview, handle_style, handle_time
from rewind.cli.interactive import interactive_mode
# Ensure the current directory is in the python path to import rewind modules
sys.path.append(os.getcwd())



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
