"""Main CLI application using Typer."""

import json
import importlib
import os
from enum import Enum
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="typer-fixtures",
    help="Generate test fixtures for your applications",
    add_completion=False,
)

console = Console()


class OutputFormat(str, Enum):
    """Output format options."""
    json = "json"
    python = "python"
    yaml = "yaml"


def get_all_generators(api_url: Optional[str] = None) -> list:
    """Dynamically discover and load all available generators."""
    generators = []

    current_dir = os.path.dirname(os.path.abspath(__file__))
    generators_dir = os.path.join(current_dir, "generators")

    if not os.path.exists(generators_dir):
        console.print(f"[yellow]Warning: Generators directory not found: {generators_dir}[/yellow]")
        return generators

    for filename in os.listdir(generators_dir):
        if filename.endswith('_generator.py') and not filename.startswith('_'):
            module_name = filename[:-3]  # Remove .py extension
            base_name = module_name.replace('_generator', '')  # Get base name without _generator

            if base_name in ['base', '__init__']:
                continue

            try:
                module = importlib.import_module(f"typer_fixtures.generators.{module_name}")

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if (isinstance(attr, type) and
                        attr_name.endswith('Generator') and
                        attr_name != 'Generator' and  # Skip the base class
                        hasattr(attr, '__init__')):

                        try:
                            generator_instance = attr(api_url)
                            generators.append((base_name, generator_instance))
                            console.print(f"[green]✓ Loaded generator: {base_name}[/green]")
                        except Exception as e:
                            console.print(f"[yellow]Warning: Could not instantiate {attr_name} from {module_name}: {e}[/yellow]")

            except Exception as e:
                console.print(f"[yellow]Warning: Could not load generator {module_name}: {e}[/yellow]")

    if not generators:
        console.print("[yellow]No generators found. Make sure you have generator classes in the generators/ directory.[/yellow]")

    return generators


@app.command()
def generate(
    output_format: OutputFormat = typer.Option(
        OutputFormat.json,
        "--format",
        "-f",
        help="Output format for the fixtures"
    ),
    save_to_file: Optional[str] = typer.Option(
        None,
        "--save",
        "-s",
        help="Save output to file instead of printing to stdout"
    ),
    list_available: bool = typer.Option(
        False,
        "--list-available",
        help="List all available fixture types"
    ),
    generator_name: Optional[str] = typer.Option(
        None,
        "--generator",
        "-g",
        help="Use specific generator (e.g., 'example', 'agent'). If not specified, uses all generators."
    )
):
    """Generate JSON fixtures using available generators."""

    generators = get_all_generators(api_url=None)  # No database needed for file generation

    if not generators:
        console.print("[red]No generators available![/red]")
        raise typer.Exit(1)

    if list_available:
        console.print("[bold blue]Available Generators and Fixture Types:[/bold blue]")
        table = Table()
        table.add_column("Generator", style="cyan")
        table.add_column("Fixture", style="green")
        table.add_column("Description", style="yellow")

        for gen_name, generator in generators:
            for fixture_name, description in generator.list_available().items():
                table.add_row(gen_name, fixture_name, description)

        console.print(table)
        return

    if generator_name:
        generators = [(name, gen) for name, gen in generators if name == generator_name]
        if not generators:
            console.print(f"[red]Generator '{generator_name}' not found![/red]")
            raise typer.Exit(1)

    try:
        all_fixtures = {}

        for gen_name, generator in generators:
            fixtures = generator.get_fixtures()
            all_fixtures[gen_name] = fixtures
            console.print(f"[green]Generated {len(fixtures)} fixtures from {gen_name} generator[/green]")

        if len(generators) == 1:
            fixtures = list(all_fixtures.values())[0]
        else:
            fixtures = []
            for gen_name, gen_fixtures in all_fixtures.items():
                for fixture in gen_fixtures:
                    fixture["_generator"] = gen_name
                fixtures.extend(gen_fixtures)

        if output_format == OutputFormat.json:
            output = json.dumps(fixtures, indent=2)
        elif output_format == OutputFormat.python:
            output = f"fixtures = {repr(fixtures)}"
        elif output_format == OutputFormat.yaml:
            import yaml
            output = yaml.dump(fixtures, default_flow_style=False)

        if save_to_file:
            with open(save_to_file, 'w') as f:
                f.write(output)
            console.print(f"[green]Saved fixtures to {save_to_file}[/green]")
        else:
            console.print(output)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def database(
    api_url: str = typer.Option(
        "http://localhost:8000",
        "--api-url",
        help="Base URL of the API"
    ),
    list_available: bool = typer.Option(
        False,
        "--list-available",
        help="List all available fixture types"
    ),
    setup: bool = typer.Option(
        True,
        "--setup/--no-setup",
        help="Create fixtures in database"
    ),
    reset: bool = typer.Option(
        False,
        "--reset",
        help="Reset all fixtures in database"
    ),
    reset_and_setup: bool = typer.Option(
        False,
        "--reset-and-setup",
        help="Reset all fixtures and recreate defaults"
    ),
    confirm: bool = typer.Option(
        False,
        "--confirm",
        help="Skip interactive confirmation (for automation)"
    ),
    list_existing: bool = typer.Option(
        False,
        "--list-existing",
        help="List existing fixtures in database"
    ),

    generator_name: Optional[str] = typer.Option(
        None,
        "--generator",
        "-g",
        help="Use specific generator (e.g., 'example', 'agent'). If not specified, uses all generators."
    )
):
    """Create, list, or reset fixtures directly in the database via API."""

    generators = get_all_generators(api_url)

    if not generators:
        console.print("[red]No generators available![/red]")
        raise typer.Exit(1)

    if list_available:
        console.print("[bold blue]Available Generators and Fixture Types:[/bold blue]")
        table = Table()
        table.add_column("Generator", style="cyan")
        table.add_column("Fixture", style="green")
        table.add_column("Description", style="yellow")

        for gen_name, generator in generators:
            for fixture_name, description in generator.list_available().items():
                table.add_row(gen_name, fixture_name, description)

        console.print(table)
        return

    if generator_name:
        generators = [(name, gen) for name, gen in generators if name == generator_name]
        if not generators:
            console.print(f"[red]Generator '{generator_name}' not found![/red]")
            raise typer.Exit(1)

    try:
        # using first generator for health check
        first_generator = generators[0][1]
        if not first_generator.health_check():
            console.print(f"[red]❌ API at {api_url} is not ready. Make sure your service is running.[/red]")
            raise typer.Exit(1)

        if list_existing:
            console.print("[bold blue]Existing Fixtures in Database:[/bold blue]")
            try:
                for gen_name, generator in generators:
                    console.print(f"\n[cyan]{gen_name.upper()} Generator:[/cyan]")
                    existing_fixtures = generator.list_existing_fixtures()
                    if existing_fixtures:
                        for fixture_id in existing_fixtures:
                            console.print(f"  • {fixture_id}")
                        console.print(f"[green]Found {len(existing_fixtures)} fixtures[/green]")
                    else:
                        console.print("[yellow]No fixtures found[/yellow]")
            except Exception as e:
                console.print(f"[red]Error listing existing fixtures: {e}[/red]")
            return

        if reset or reset_and_setup:
            if reset_and_setup:
                console.print("[bold red]⚠️  WARNING: This will DELETE all fixtures and recreate defaults![/bold red]")
                console.print("This action cannot be undone.")

                if not confirm:
                    if not typer.confirm("Are you sure you want to continue?"):
                        console.print("[yellow]Reset cancelled.[/yellow]")
                        raise typer.Exit(0)

                console.print("[yellow]🔄 Resetting all fixtures and recreating defaults...[/yellow]")

                total_created = 0
                for gen_name, generator in generators:
                    console.print(f"\n[cyan]Processing {gen_name} generator...[/cyan]")
                    result = generator.reset_and_setup(confirm=True)
                    if result["status"] == "warning":
                        console.print(f"[yellow]⚠️ {result['reset']['message']}[/yellow]")
                    else:
                        console.print(f"[green]✅ {result['reset']['message']}[/green]")

                    created_fixtures = result.get('created_fixtures', [])
                    total_created += len(created_fixtures)
                    if len(created_fixtures) > 0:
                        console.print(f"[green]✅ Created {len(created_fixtures)} new fixtures[/green]")
                        for fixture in created_fixtures:
                            console.print(f"  • {fixture['fixture_id']}")
                    else:
                        console.print(f"[yellow]⚠️ No new fixtures created[/yellow]")

                console.print(f"\n[bold green]🎉 Total: Created {total_created} fixtures across all generators[/bold green]")

            elif reset:
                console.print("[bold red]⚠️  WARNING: This will DELETE all fixtures from the database![/bold red]")
                console.print("This action cannot be undone.")

                if not confirm:
                    if not typer.confirm("Are you sure you want to continue?"):
                        console.print("[yellow]Reset cancelled.[/yellow]")
                        raise typer.Exit(0)

                console.print("[yellow]🔄 Resetting all fixtures...[/yellow]")

                total_deleted = 0
                for gen_name, generator in generators:
                    console.print(f"\n[cyan]Processing {gen_name} generator...[/cyan]")
                    result = generator.reset_fixtures(confirm=True)
                    if result["status"] == "warning":
                        console.print(f"[yellow]⚠️ {result['reset']['message']}[/yellow]")
                    else:
                        console.print(f"[green]✅ {result['reset']['message']}[/green]")

                    total_deleted += result.get('count', 0)
                    if result.get('fixtures_deleted'):
                        console.print("[yellow]Deleted fixtures:[/yellow]")
                        for fixture_id in result['fixtures_deleted']:
                            console.print(f"  • {fixture_id}")

                console.print(f"\n[bold green]🎉 Total: Deleted {total_deleted} fixtures across all generators[/bold green]")

        elif setup:
            console.print("[yellow]🔄 Setting up fixtures in database...[/yellow]")

            total_created = 0
            for gen_name, generator in generators:
                console.print(f"\n[cyan]Processing {gen_name} generator...[/cyan]")
                created_fixtures = generator.setup_fixtures()
                total_created += len(created_fixtures)
                console.print(f"[green]✅ Created {len(created_fixtures)} fixtures in database[/green]")
                for fixture in created_fixtures:
                    console.print(f"  • {fixture['fixture_id']}")

            console.print(f"\n[bold green]🎉 Total: Created {total_created} fixtures across all generators[/bold green]")

    except ValueError as e:
        console.print(f"[red]❌ {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def list_commands():
    """List all available commands and their purposes."""
    console.print("[bold blue]Available Commands:[/bold blue]")
    console.print("• [cyan]generate[/cyan] - Generate JSON fixtures for testing")
    console.print("• [cyan]database[/cyan] - Create, list, or reset fixtures in database via API")
    console.print("• [cyan]list-commands[/cyan] - Show this help")
    console.print("")
    console.print("[bold yellow]Generator Options:[/bold yellow]")
    console.print("• [cyan]--generator[/cyan] - Use specific generator (e.g., 'example', 'agent')")
    console.print("• [cyan]--list-available[/cyan] - List available generators and fixture types")
    console.print("")
    console.print("[bold yellow]Database Command Options:[/bold yellow]")
    console.print("• [cyan]--list-existing[/cyan] - List existing fixtures in database")
    console.print("• [cyan]--setup[/cyan] - Create fixtures (default)")
    console.print("• [cyan]--reset[/cyan] - Reset all fixtures (interactive confirmation)")
    console.print("• [cyan]--reset-and-setup[/cyan] - Reset and recreate defaults (interactive confirmation)")
    console.print("• [cyan]--confirm[/cyan] - Skip interactive confirmation (for automation)")



if __name__ == "__main__":
    app()