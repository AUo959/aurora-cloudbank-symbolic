"""Configuration command group."""

import os
from pathlib import Path
from typing import Optional

import typer
import yaml
from rich import print as rprint
from rich.table import Table

app = typer.Typer(help="Configuration management")


CONFIG_DIR = Path.home() / ".aurora"
CONFIG_FILE = CONFIG_DIR / "config.yaml"


def ensure_config_dir() -> None:
    """Ensure configuration directory exists."""
    CONFIG_DIR.mkdir(exist_ok=True)


def load_config() -> dict:
    """Load configuration from file."""
    if not CONFIG_FILE.exists():
        return {}

    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f) or {}


def save_config(config: dict) -> None:
    """Save configuration to file."""
    ensure_config_dir()

    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f, default_flow_style=False)


@app.command("set")
def set_config(
    key: str = typer.Argument(..., help="Configuration key"),
    value: str = typer.Argument(..., help="Configuration value"),
) -> None:
    """Set a configuration value.

    Examples:
        aurora config set api_key sk_live_...
        aurora config set base_url https://api.aurora.dev
    """
    config = load_config()
    config[key] = value
    save_config(config)

    rprint(f"[green]✓ Set {key} = {value}[/green]")

    # Also set environment variable
    os.environ[f"AURORA_{key.upper()}"] = value


@app.command("get")
def get_config(key: str = typer.Argument(..., help="Configuration key")) -> None:
    """Get a configuration value.

    Examples:
        aurora config get api_key
        aurora config get base_url
    """
    config = load_config()

    if key in config:
        # Redact API key
        value = config[key]
        if key == "api_key" and len(value) > 10:
            value = f"{value[:7]}...{value[-3:]}"

        rprint(f"{key}: {value}")
    else:
        rprint(f"[yellow]Configuration key '{key}' not found[/yellow]")


@app.command("list")
def list_config() -> None:
    """List all configuration values.

    Examples:
        aurora config list
    """
    config = load_config()

    if not config:
        rprint("[yellow]No configuration found[/yellow]")
        rprint(f"Configuration file: {CONFIG_FILE}")
        return

    table = Table(title="Aurora Configuration")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="white")

    for key, value in config.items():
        # Redact API key
        if key == "api_key" and len(str(value)) > 10:
            value = f"{value[:7]}...{value[-3:]}"

        table.add_row(key, str(value))

    from rich.console import Console
    console = Console()
    console.print(table)

    rprint(f"\n[dim]Configuration file: {CONFIG_FILE}[/dim]")


@app.command("validate")
def validate_config() -> None:
    """Validate configuration.

    Examples:
        aurora config validate
    """
    config = load_config()

    errors = []

    # Check required fields
    if "api_key" not in config:
        errors.append("Missing required field: api_key")

    # Check API key format
    if "api_key" in config:
        api_key = config["api_key"]
        if not api_key.startswith("sk_"):
            errors.append("API key should start with 'sk_'")

    # Check base_url format
    if "base_url" in config:
        base_url = config["base_url"]
        if not base_url.startswith("http"):
            errors.append("base_url should start with 'http://' or 'https://'")

    if errors:
        rprint("[bold red]Configuration validation failed:[/bold red]")
        for error in errors:
            rprint(f"  ✗ {error}")
        raise typer.Exit(1)
    else:
        rprint("[bold green]✓ Configuration is valid[/bold green]")
