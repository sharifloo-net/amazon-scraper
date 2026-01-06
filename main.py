#!/usr/bin/env python3
"""Amazon Price Tracker - Command Line Interface

Scrape and track Amazon product prices with options for one-time or daily runs.
"""
import logging

import typer
from rich.console import Console
from rich.logging import RichHandler

from config import LOG_LEVEL
from runners.run_daily import run_daily
from runners.run_once import run_once

# Initialize Typer app
app = typer.Typer(
    help="Amazon Price Tracker - Scrape and monitor product prices",
    add_completion=False,  # Disable shell completion for simplicity
)

# Set up console for pretty output
console = Console()
error_console = Console(stderr=True)

# Configure logging
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=error_console, rich_tracebacks=True)]
)
logger = logging.getLogger(__name__)

def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print("Amazon Price Tracker v1.0.0", style="bold green")
        raise typer.Exit()

@app.callback()
def main(
    verbose: int = typer.Option(
        0, "--verbose", "-v", 
        count=True,
        help="Increase verbosity (can be used multiple times)"
    ),
    version: bool = typer.Option(
        None, 
        "--version", 
        callback=version_callback,
        is_eager=True,
        help="Show version and exit."
    )
):
    """Amazon Price Tracker - Monitor product prices on Amazon."""
    # Set logging level based on verbosity
    log_levels = [logging.WARNING, logging.INFO, logging.DEBUG]
    log_level = log_levels[min(verbose, len(log_levels) - 1)]
    logging.getLogger().setLevel(log_level)
    
    if verbose > 0:
        logger.info(f"Verbosity set to {logging.getLevelName(log_level)}")

@app.command(help="Run scraping once and export results")
def once():
    """Run scraping once and export results."""
    try:
        with console.status("[bold green]Running one-time scrape..."):
            logger.info("Starting one-time scrape")
            run_once()
        console.print("✅ [bold green]Scraping completed successfully![/bold green]")
    except Exception as e:
        error_console.print(f"❌ [bold red]Error:[/bold red] {e}")
        if logger.level <= logging.DEBUG:
            logger.exception("Detailed error:")
        raise typer.Exit(1)

@app.command(help="Run scraping and generate daily report")
def daily():
    """Run scraping and generate daily report."""
    try:
        with console.status("[bold green]Running daily scrape..."):
            logger.info("Starting daily scrape")
            run_daily()
        console.print("✅ [bold green]Daily scraping completed![/bold green]")
    except Exception as e:
        error_console.print(f"❌ [bold red]Error:[/bold red] {e}")
        if logger.level <= logging.DEBUG:
            logger.exception("Detailed error:")
        raise typer.Exit(1)

if __name__ == "__main__":
    app()
