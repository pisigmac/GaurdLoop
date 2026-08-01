"""CLI utilities."""
import json
import click
from typing import List

def print_json(data: dict):
    click.echo(json.dumps(data, indent=2, default=str))

def print_success(message: str):
    click.echo(click.style(f"✓ {message}", fg="green"))

def print_error(message: str):
    click.echo(click.style(f"✗ {message}", fg="red"), err=True)

def print_table(headers: List[str], rows: List[List[str]]):
    # Simple table formatting
    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells):
        return "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(cells))

    click.echo(fmt_row(headers))
    click.echo("-" * (sum(col_widths) + 2 * (len(headers) - 1)))
    for row in rows:
        click.echo(fmt_row(row))
