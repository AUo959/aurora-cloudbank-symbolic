"""Main Aurora CLI application."""

import asyncio
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.table import Table

from aurora_cli import __version__
from aurora_cli.commands import config, scenario

# Create CLI app
app = typer.Typer(
    name="aurora",
    help="Aurora CloudBank Symbolic - Quantum-Symbolic Computing Platform CLI",
    add_completion=True,
    rich_markup_mode="rich",
)

# Add command groups
app.add_typer(scenario.app, name="scenario", help="Quantum scenario operations")
app.add_typer(config.app, name="config", help="Configuration management")

# Create console for rich output
console = Console()


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        rprint(f"[bold]Aurora CLI[/bold] version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        help="Show version and exit"
    )
) -> None:
    """Aurora CloudBank Symbolic CLI.

    A unified command-line interface for Aurora quantum-symbolic computing platform.

    Examples:
        aurora scenario run supply_chain --param suppliers=5
        aurora config set api_key sk_test_...
        aurora memory create "Important note" --tag note
    """
    pass


@app.command()
def init(
    project_name: Optional[str] = typer.Argument(None, help="Project name"),
    template: str = typer.Option("python", help="Project template (python, javascript, docker)"),
    path: Optional[str] = typer.Option(None, help="Project directory"),
) -> None:
    """Initialize a new Aurora project.

    Examples:
        aurora init my-quantum-app
        aurora init my-app --template python
        aurora init . --template javascript
    """
    from aurora_cli.commands.init import init_project

    init_project(project_name, template, path)


@app.command()
def dev(
    port: int = typer.Option(8000, help="Port number"),
    playground: bool = typer.Option(False, help="Start with playground UI"),
    docs: bool = typer.Option(False, help="Start with documentation"),
) -> None:
    """Start development server.

    Examples:
        aurora dev
        aurora dev --port 3000 --playground
        aurora dev --docs
    """
    from aurora_cli.commands.dev import start_dev_server

    start_dev_server(port, playground, docs)


@app.command()
def playground() -> None:
    """Open playground in browser.

    Opens the Aurora interactive playground at https://playground.aurora.dev
    """
    import webbrowser

    url = "https://playground.aurora.dev"
    rprint(f"[bold green]Opening playground at {url}...[/bold green]")
    webbrowser.open(url)


@app.command()
def docs(topic: Optional[str] = typer.Argument(None, help="Documentation topic")) -> None:
    """Open documentation in browser.

    Examples:
        aurora docs
        aurora docs scenarios
        aurora docs api
    """
    import webbrowser

    base_url = "https://developers.aurora.dev"
    url = f"{base_url}/{topic}" if topic else base_url

    rprint(f"[bold green]Opening documentation at {url}...[/bold green]")
    webbrowser.open(url)


@app.command()
def status() -> None:
    """Show Aurora environment status.

    Displays configuration, authentication status, and system information.
    """
    from aurora_cli.commands.status import show_status

    show_status()


if __name__ == "__main__":
    app()
