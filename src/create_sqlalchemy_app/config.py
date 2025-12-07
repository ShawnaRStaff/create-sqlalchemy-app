"""
Project configuration management.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class Framework(Enum):
    """Supported web frameworks."""
    FASTAPI = "fastapi"
    FLASK = "flask"
    MINIMAL = "minimal"

    @property
    def display_name(self) -> str:
        """Human-readable name for display."""
        names = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "minimal": "Minimal (no web framework)"
        }
        return names.get(self.value, self.value)

    @property
    def description(self) -> str:
        """Description for CLI selection."""
        descriptions = {
            "fastapi": "Async, auto-docs, modern API framework",
            "flask": "Flexible, traditional web framework",
            "minimal": "Just SQLAlchemy + Alembic, no web framework"
        }
        return descriptions.get(self.value, "")


class Database(Enum):
    """Supported databases."""
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"
    MYSQL = "mysql"

    @property
    def display_name(self) -> str:
        """Human-readable name for display."""
        names = {
            "postgresql": "PostgreSQL",
            "sqlite": "SQLite",
            "mysql": "MySQL/MariaDB"
        }
        return names.get(self.value, self.value)

    @property
    def description(self) -> str:
        """Description for CLI selection."""
        descriptions = {
            "postgresql": "Recommended for production, full-featured",
            "sqlite": "Simple file-based, great for development",
            "mysql": "Popular, widely supported"
        }
        return descriptions.get(self.value, "")

    @property
    def default_port(self) -> str:
        """Default port for database."""
        ports = {
            "postgresql": "5432",
            "sqlite": "",
            "mysql": "3306"
        }
        return ports.get(self.value, "")

    @property
    def driver(self) -> str:
        """SQLAlchemy driver string."""
        drivers = {
            "postgresql": "postgresql",
            "sqlite": "sqlite",
            "mysql": "mysql+pymysql"
        }
        return drivers.get(self.value, "")

    @property
    def requires_server(self) -> bool:
        """Whether this database requires a running server."""
        return self.value != "sqlite"


@dataclass
class ProjectConfig:
    """Configuration for a new project."""

    # Project basics
    name: str
    path: Path

    # Framework selection
    framework: Framework = Framework.MINIMAL

    # Database configuration
    database: Database = Database.POSTGRESQL
    db_name: str = "mydb"
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_host: str = "localhost"
    db_port: str = "5432"

    # Feature flags
    include_docker: bool = True
    include_tests: bool = True
    include_erd_generator: bool = True
    include_data_import: bool = True
    init_git: bool = True
    create_database: bool = False

    # Starter kit (for future use)
    starter: Optional[str] = None

    # Computed fields
    venv_name: str = field(init=False)

    def __post_init__(self):
        """Set computed fields after initialization."""
        self.venv_name = ".venv"

        # Convert path to Path object if string
        if isinstance(self.path, str):
            self.path = Path(self.path)

        # Set default port based on database if not specified
        if not self.db_port and self.database.requires_server:
            self.db_port = self.database.default_port

    @property
    def venv_path(self) -> Path:
        """Get the virtual environment path."""
        return self.path / self.venv_name

    @property
    def database_url(self) -> str:
        """Get the database URL."""
        if self.database == Database.SQLITE:
            return f"sqlite:///{self.db_name}.db"
        elif self.database == Database.MYSQL:
            return f"mysql+pymysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:  # PostgreSQL
            return f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    @property
    def async_database_url(self) -> str:
        """Get async database URL (for FastAPI async support)."""
        if self.database == Database.SQLITE:
            return f"sqlite+aiosqlite:///{self.db_name}.db"
        elif self.database == Database.MYSQL:
            return f"mysql+aiomysql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        else:  # PostgreSQL
            return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"

    def get_dependencies(self) -> List[str]:
        """Get list of dependencies based on configuration."""
        # Core dependencies (always included)
        deps = [
            "alembic",
            "python-dotenv",
            "sqlalchemy>=2.0.0",
        ]

        # Database-specific drivers
        if self.database == Database.POSTGRESQL:
            deps.extend([
                "psycopg[binary]",
                "psycopg2-binary",
            ])
        elif self.database == Database.MYSQL:
            deps.append("pymysql")
        # SQLite uses built-in driver

        # Framework-specific dependencies
        if self.framework == Framework.FASTAPI:
            deps.extend([
                "fastapi",
                "uvicorn[standard]",
                "python-multipart",
                "httpx",
            ])
        elif self.framework == Framework.FLASK:
            deps.extend([
                "flask",
                "flask-sqlalchemy",
            ])

        # Optional features
        if self.include_data_import:
            deps.extend([
                "pandas",
                "tqdm",
            ])

        if self.include_tests:
            deps.extend([
                "pytest",
                "pytest-cov",
            ])
            if self.framework == Framework.FASTAPI:
                deps.append("pytest-asyncio")

        return sorted(set(deps))

    def to_template_context(self) -> Dict[str, Any]:
        """Get context for template rendering."""
        return {
            "project_name": self.name,
            "framework": self.framework.value,
            "framework_display": self.framework.display_name,
            "database": self.database.value,
            "database_display": self.database.display_name,
            "database_driver": self.database.driver,
            "db_name": self.db_name,
            "db_user": self.db_user,
            "db_password": self.db_password,
            "db_host": self.db_host,
            "db_port": self.db_port,
            "database_url": self.database_url,
            "async_database_url": self.async_database_url,
            "venv_name": self.venv_name,
            "include_docker": self.include_docker,
            "include_tests": self.include_tests,
            "include_erd_generator": self.include_erd_generator,
            "include_data_import": self.include_data_import,
            "requires_server": self.database.requires_server,
            "is_fastapi": self.framework == Framework.FASTAPI,
            "is_flask": self.framework == Framework.FLASK,
            "is_minimal": self.framework == Framework.MINIMAL,
            "is_postgresql": self.database == Database.POSTGRESQL,
            "is_sqlite": self.database == Database.SQLITE,
            "is_mysql": self.database == Database.MYSQL,
        }
