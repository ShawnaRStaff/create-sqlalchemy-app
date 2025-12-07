#!/usr/bin/env python3
"""
Create SQLAlchemy App - CLI Entry Point

A CLI tool to scaffold SQLAlchemy projects with a single command.
Similar to Create React App, but for Python backends.
"""

import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import print as rprint

from .config import ProjectConfig, Framework, Database
from .generator import ProjectGenerator

console = Console()

LOGO = r"""
   ___                _        ___  ___  _      _   _    _
  / __| _ _  ___  __ _| |_ ___ / __|/ _ \| |    /_\ | |__| |_  ___ _ __  _  _
 | (__ | '_|/ -_)/ _` |  _/ -_)\__ \ (_) | |__ / _ \| / _| ' \/ -_) '  \| || |
  \___|_|  \___|\__,_|\__\___||___/\__\_\____/_/ \_\_\__|_||_\___|_|_|_|\_, |
                                                                        |__/
                                                                         v1.0.0
"""


def display_welcome():
    """Display welcome message and logo."""
    console.print(Panel(LOGO, style="bold blue", border_style="blue"))
    console.print()


def display_success(project_name: str, project_path: Path, config: ProjectConfig):
    """Display success message with next steps."""
    console.print()
    console.print(Panel(
        f"[bold green]Success![/bold green] Created [bold]{project_name}[/bold] at [cyan]{project_path}[/cyan]",
        border_style="green"
    ))

    console.print()
    console.print("[bold]Next steps:[/bold]")
    console.print()

    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column("Step", style="cyan")
    table.add_column("Command", style="green")

    step = 1
    table.add_row(f"{step}. Navigate to project:", f"cd {project_name}")
    step += 1

    # Docker step (if applicable)
    if config.include_docker and config.database.requires_server:
        table.add_row(f"{step}. Start database:", "docker-compose up -d")
        step += 1

    # Activate venv
    table.add_row(f"{step}. Activate virtual environment:",
                  f"source {config.venv_name}/bin/activate  [dim](Unix)[/dim]")
    table.add_row("   or:",
                  f".\\{config.venv_name}\\Scripts\\activate  [dim](Windows)[/dim]")
    step += 1

    # Create models reminder
    table.add_row(f"{step}. Create your models:", "Edit files in models/")
    step += 1

    # Migration steps
    table.add_row(f"{step}. Create initial migration:",
                  'alembic revision --autogenerate -m "Initial migration"')
    step += 1
    table.add_row(f"{step}. Apply migration:", "alembic upgrade head")
    step += 1

    # Run tests (if included)
    if config.include_tests:
        table.add_row(f"{step}. Run tests:", "pytest -xvs")

    console.print(table)
    console.print()

    # CSV import warning if included
    if config.include_data_import:
        console.print(Panel(
            "[yellow]CSV Import Note:[/yellow]\n\n"
            "The CSV import module is included at [cyan]scripts/data_import.py[/cyan]\n\n"
            "[bold]Before importing data, you must:[/bold]\n"
            "  1. Create SQLAlchemy models matching your CSV structure\n"
            "  2. Define appropriate indexes and constraints\n"
            "  3. Update column mappings in the import script\n"
            "  4. Run migrations to create tables\n\n"
            "See [cyan]docs/CSV_IMPORT.md[/cyan] for detailed instructions.",
            title="[yellow]Important[/yellow]",
            border_style="yellow"
        ))
        console.print()

    console.print("[dim]Happy coding![/dim]")


def prompt_framework() -> Framework:
    """Prompt user to select a framework."""
    console.print("[bold]Select your framework:[/bold]")
    console.print()

    options = [
        ("1", Framework.FASTAPI, "FastAPI", "Async, auto-docs, modern API framework"),
        ("2", Framework.FLASK, "Flask", "Flexible, traditional web framework"),
        ("3", Framework.MINIMAL, "Minimal", "Just SQLAlchemy + Alembic, no web framework"),
    ]

    for num, _, name, desc in options:
        console.print(f"  [cyan]{num}[/cyan]) [bold]{name}[/bold] - {desc}")

    console.print()
    choice = Prompt.ask(
        "Enter your choice",
        choices=["1", "2", "3"],
        default="1"
    )

    framework_map = {"1": Framework.FASTAPI, "2": Framework.FLASK, "3": Framework.MINIMAL}
    return framework_map[choice]


def prompt_database() -> Database:
    """Prompt user to select a database."""
    console.print()
    console.print("[bold]Select your database:[/bold]")
    console.print()

    options = [
        ("1", Database.POSTGRESQL, "PostgreSQL", "Recommended for production, full-featured"),
        ("2", Database.SQLITE, "SQLite", "Simple file-based, great for development"),
        ("3", Database.MYSQL, "MySQL/MariaDB", "Popular, widely supported"),
    ]

    for num, _, name, desc in options:
        console.print(f"  [cyan]{num}[/cyan]) [bold]{name}[/bold] - {desc}")

    console.print()
    choice = Prompt.ask(
        "Enter your choice",
        choices=["1", "2", "3"],
        default="1"
    )

    db_map = {"1": Database.POSTGRESQL, "2": Database.SQLITE, "3": Database.MYSQL}
    return db_map[choice]


def prompt_database_config(database: Database) -> dict:
    """Prompt for database configuration."""
    config = {}

    console.print()
    console.print("[bold]Database configuration:[/bold]")
    console.print()

    config["db_name"] = Prompt.ask(
        "  [cyan]Database name[/cyan]",
        default="mydb"
    )

    if database.requires_server:
        config["db_user"] = Prompt.ask(
            "  [cyan]Database user[/cyan]",
            default="postgres" if database == Database.POSTGRESQL else "root"
        )

        config["db_password"] = Prompt.ask(
            "  [cyan]Database password[/cyan]",
            default="postgres" if database == Database.POSTGRESQL else "root",
            password=True
        )

        config["db_host"] = Prompt.ask(
            "  [cyan]Database host[/cyan]",
            default="localhost"
        )

        config["db_port"] = Prompt.ask(
            "  [cyan]Database port[/cyan]",
            default=database.default_port
        )
    else:
        # SQLite doesn't need these
        config["db_user"] = ""
        config["db_password"] = ""
        config["db_host"] = ""
        config["db_port"] = ""

    return config


def prompt_features(database: Database) -> dict:
    """Prompt for optional features."""
    config = {}

    console.print()
    console.print("[bold]Optional features:[/bold]")
    console.print()

    if database.requires_server:
        config["include_docker"] = Confirm.ask(
            "  [cyan]Include Docker setup for database?[/cyan]",
            default=True
        )
    else:
        config["include_docker"] = False

    config["include_tests"] = Confirm.ask(
        "  [cyan]Include test suite?[/cyan]",
        default=True
    )

    config["include_erd_generator"] = Confirm.ask(
        "  [cyan]Include ERD generator?[/cyan]",
        default=True
    )

    config["include_data_import"] = Confirm.ask(
        "  [cyan]Include CSV data import module?[/cyan]",
        default=True
    )

    config["init_git"] = Confirm.ask(
        "  [cyan]Initialize Git repository?[/cyan]",
        default=True
    )

    if database.requires_server and not config.get("include_docker"):
        config["create_database"] = Confirm.ask(
            "  [cyan]Create database now? (requires running DB server)[/cyan]",
            default=False
        )
    else:
        config["create_database"] = False

    return config


@click.command()
@click.argument("project_name", required=False)
@click.option(
    "--directory", "-d",
    type=click.Path(),
    default=".",
    help="Parent directory for the project (default: current directory)"
)
@click.option(
    "--framework", "-f",
    type=click.Choice(["fastapi", "flask", "minimal"]),
    help="Web framework to use"
)
@click.option(
    "--database", "-db",
    type=click.Choice(["postgresql", "sqlite", "mysql"]),
    help="Database to use"
)
@click.option(
    "--db-name",
    type=str,
    help="Database name"
)
@click.option(
    "--db-user",
    type=str,
    help="Database user"
)
@click.option(
    "--db-password",
    type=str,
    help="Database password"
)
@click.option(
    "--db-host",
    type=str,
    default="localhost",
    help="Database host (default: localhost)"
)
@click.option(
    "--db-port",
    type=str,
    help="Database port"
)
@click.option(
    "--no-docker",
    is_flag=True,
    help="Skip Docker setup"
)
@click.option(
    "--no-tests",
    is_flag=True,
    help="Skip test suite"
)
@click.option(
    "--no-git",
    is_flag=True,
    help="Skip Git initialization"
)
@click.option(
    "--no-erd",
    is_flag=True,
    help="Skip ERD generator"
)
@click.option(
    "--no-csv-import",
    is_flag=True,
    help="Skip CSV import module"
)
@click.option(
    "--yes", "-y",
    is_flag=True,
    help="Skip interactive prompts (requires --framework and --database)"
)
@click.version_option(version="1.0.0", prog_name="create-sqlalchemy-app")
def main(
    project_name: str,
    directory: str,
    framework: str,
    database: str,
    db_name: str,
    db_user: str,
    db_password: str,
    db_host: str,
    db_port: str,
    no_docker: bool,
    no_tests: bool,
    no_git: bool,
    no_erd: bool,
    no_csv_import: bool,
    yes: bool
):
    """
    Create a new SQLAlchemy project with a single command.

    \b
    Examples:
        create-sqlalchemy-app my-project
        csa my-project --framework fastapi --database postgresql
        csa my-project -f minimal -db sqlite -y
    """
    display_welcome()

    # Get project name if not provided
    if not project_name:
        project_name = Prompt.ask(
            "[bold cyan]What is your project named?[/bold cyan]"
        )
        if not project_name:
            console.print("[red]Error: Project name is required[/red]")
            sys.exit(1)

    # Validate project name
    if not project_name.replace("-", "").replace("_", "").isalnum():
        console.print(
            "[red]Error: Project name can only contain letters, numbers, hyphens, and underscores[/red]"
        )
        sys.exit(1)

    project_path = Path(directory).absolute() / project_name

    # Check if directory exists
    if project_path.exists():
        if not Confirm.ask(f"[yellow]Directory {project_path} already exists. Continue?[/yellow]"):
            console.print("[dim]Aborted.[/dim]")
            sys.exit(0)

    # Non-interactive mode validation
    if yes and (not framework or not database):
        console.print(
            "[red]Error: --yes requires both --framework and --database to be specified[/red]"
        )
        sys.exit(1)

    # Gather configuration
    if yes:
        # Non-interactive mode
        selected_framework = Framework(framework)
        selected_database = Database(database)

        db_config = {
            "db_name": db_name or project_name.replace("-", "_"),
            "db_user": db_user or ("postgres" if selected_database == Database.POSTGRESQL else "root"),
            "db_password": db_password or ("postgres" if selected_database == Database.POSTGRESQL else "root"),
            "db_host": db_host,
            "db_port": db_port or selected_database.default_port,
        }

        feature_config = {
            "include_docker": not no_docker and selected_database.requires_server,
            "include_tests": not no_tests,
            "include_erd_generator": not no_erd,
            "include_data_import": not no_csv_import,
            "init_git": not no_git,
            "create_database": False,
        }
    else:
        # Interactive mode
        selected_framework = prompt_framework()
        selected_database = prompt_database()
        db_config = prompt_database_config(selected_database)
        feature_config = prompt_features(selected_database)

    # Create project configuration
    project_config = ProjectConfig(
        name=project_name,
        path=project_path,
        framework=selected_framework,
        database=selected_database,
        **db_config,
        **feature_config
    )

    console.print()

    # Generate project
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        generator = ProjectGenerator(project_config, progress)

        try:
            generator.generate()
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            import traceback
            traceback.print_exc()
            sys.exit(1)

    display_success(project_name, project_path, project_config)


if __name__ == "__main__":
    main()
