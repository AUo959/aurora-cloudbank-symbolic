"""Scenario command group."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from aurora_sdk import AuroraClient

app = typer.Typer(help="Quantum scenario operations")
console = Console()


@app.command("run")
def run_scenario(
    scenario: str = typer.Argument(..., help="Scenario name"),
    config_file: Optional[Path] = typer.Option(None, "--config", help="Config JSON file"),
    param: Optional[list[str]] = typer.Option(None, "--param", help="Parameter (key=value)"),
    output: Optional[Path] = typer.Option(None, "--output", help="Output file"),
    format: str = typer.Option("text", help="Output format (text, json)"),
) -> None:
    """Run a quantum scenario.

    Examples:
        aurora scenario run supply_chain --param suppliers=5
        aurora scenario run supply_chain --config scenario.json
        aurora scenario run energy_grid --output result.json
    """
    asyncio.run(_run_scenario(scenario, config_file, param, output, format))


async def _run_scenario(
    scenario: str,
    config_file: Optional[Path],
    param: Optional[list[str]],
    output: Optional[Path],
    format: str,
) -> None:
    """Run scenario (async implementation)."""
    # Parse parameters
    params = {}

    if config_file:
        with open(config_file) as f:
            data = json.load(f)
            params = data.get("params", {})

    if param:
        for p in param:
            if "=" not in p:
                rprint(f"[red]Error: Invalid parameter format: {p}[/red]")
                rprint("Use --param key=value")
                raise typer.Exit(1)

            key, value = p.split("=", 1)
            # Try to parse as JSON, fallback to string
            try:
                params[key] = json.loads(value)
            except json.JSONDecodeError:
                params[key] = value

    # Run scenario
    async with AuroraClient() as client:
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Running scenario {scenario}...", total=None)

            try:
                result = await client.quantum.run_scenario(scenario, **params)
                progress.update(task, description="[bold green]✓ Scenario completed")

            except Exception as e:
                progress.update(task, description=f"[bold red]✗ Error: {e}")
                raise typer.Exit(1)

    # Output result
    if format == "json" or output:
        result_json = result.to_dict()

        if output:
            with open(output, "w") as f:
                json.dump(result_json, f, indent=2)
            rprint(f"[green]✓ Results saved to {output}[/green]")
        else:
            rprint(json.dumps(result_json, indent=2))

    else:
        # Text output
        rprint("\n[bold]Scenario Result[/bold]")
        rprint(f"Scenario ID: {result.scenario_id}")
        rprint(f"Status: [green]{result.status}[/green]")
        rprint(f"Optimal State: {result.optimal_state}")
        rprint(f"Execution Time: {result.execution_time:.2f}s")

        if result.metrics:
            rprint("\n[bold]Metrics:[/bold]")
            for key, value in result.metrics.items():
                if isinstance(value, float):
                    rprint(f"  {key}: {value:.2f}")
                else:
                    rprint(f"  {key}: {value}")


@app.command("list")
def list_scenarios() -> None:
    """List available quantum scenarios.

    Examples:
        aurora scenario list
    """
    asyncio.run(_list_scenarios())


async def _list_scenarios() -> None:
    """List scenarios (async implementation)."""
    async with AuroraClient() as client:
        scenarios = await client.quantum.list_scenarios()

    table = Table(title="Available Quantum Scenarios")
    table.add_column("Scenario", style="cyan")
    table.add_column("Description", style="white")

    scenario_descriptions = {
        "supply_chain_optimization": "Optimize supply chain logistics",
        "energy_grid_balancing": "Balance energy grid loads",
        "risk_assessment": "Assess portfolio risk",
        "portfolio_optimization": "Optimize investment portfolios",
        "network_routing": "Optimize network routing",
        "resource_allocation": "Allocate resources efficiently",
        "scheduling": "Schedule tasks optimally",
    }

    for scenario in scenarios:
        desc = scenario_descriptions.get(scenario, "Quantum optimization scenario")
        table.add_row(scenario, desc)

    console.print(table)


@app.command("template")
def scenario_template(scenario: str = typer.Argument(..., help="Scenario name")) -> None:
    """Get scenario configuration template.

    Examples:
        aurora scenario template supply_chain > my_scenario.json
    """
    template = {
        "scenario": scenario,
        "params": {
            "num_suppliers": 5,
            "demand_variance": 0.2,
            "cost_weights": [0.3, 0.4, 0.2, 0.5, 0.3]
        }
    }

    rprint(json.dumps(template, indent=2))
