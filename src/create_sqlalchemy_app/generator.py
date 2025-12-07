"""
Project generator - creates the project structure and files.
"""

import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Optional

from jinja2 import Environment, PackageLoader, select_autoescape
from rich.progress import Progress, TaskID

from .config import ProjectConfig, Framework, Database


class ProjectGenerator:
    """Generates a new SQLAlchemy project."""

    def __init__(self, config: ProjectConfig, progress: Optional[Progress] = None):
        self.config = config
        self.progress = progress
        self.is_windows = platform.system() == "Windows"

        # Setup Jinja2 environment
        self.env = Environment(
            loader=PackageLoader("create_sqlalchemy_app", "templates"),
            autoescape=select_autoescape(),
            keep_trailing_newline=True,
        )

        # Python executables
        self.python_cmd = "python" if self.is_windows else "python3"
        self._task_id = None

    def _update_progress(self, description: str):
        """Update progress display."""
        if self.progress and self._task_id is not None:
            self.progress.update(self._task_id, description=description)

    def _run_command(
        self, command: list, cwd: Optional[Path] = None, check: bool = True
    ) -> subprocess.CompletedProcess:
        """Run a shell command."""
        return subprocess.run(
            command,
            cwd=cwd or self.config.path,
            check=check,
            text=True,
            capture_output=True,
        )

    def _get_python_executable(self) -> str:
        """Get the path to the virtual environment's Python executable."""
        if self.is_windows:
            return str(self.config.venv_path / "Scripts" / "python.exe")
        return str(self.config.venv_path / "bin" / "python")

    def _render_template(self, template_name: str, **extra_context) -> str:
        """Render a Jinja2 template."""
        template = self.env.get_template(template_name)
        context = self.config.to_template_context()
        context.update(extra_context)
        return template.render(**context)

    def _write_file(self, relative_path: str, content: str):
        """Write content to a file in the project directory."""
        file_path = self.config.path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")

    def generate(self):
        """Generate the complete project."""
        if self.progress:
            self._task_id = self.progress.add_task("Creating project...", total=None)

        # Step 1: Create directory structure
        self._update_progress("Creating directory structure...")
        self._create_directories()

        # Step 2: Create virtual environment
        self._update_progress("Creating virtual environment...")
        self._create_virtual_environment()

        # Step 3: Install dependencies
        self._update_progress("Installing dependencies...")
        self._install_dependencies()

        # Step 4: Generate project files
        self._update_progress("Generating project files...")
        self._generate_files()

        # Step 5: Initialize Alembic
        self._update_progress("Initializing Alembic...")
        self._initialize_alembic()

        # Step 6: Create database (optional)
        if self.config.create_database and self.config.database.requires_server:
            self._update_progress("Creating database...")
            self._create_database()

        # Step 7: Initialize Git (optional)
        if self.config.init_git:
            self._update_progress("Initializing Git repository...")
            self._initialize_git()

        self._update_progress("Complete!")

    def _create_directories(self):
        """Create the project directory structure."""
        directories = [
            "migrations/versions",
            "scripts",
            "data",
            "models",
            "docs",
        ]

        if self.config.include_tests:
            directories.extend([
                "tests/integration_tests",
                "tests/unit_tests",
            ])

        if self.config.include_erd_generator:
            directories.append("docs/erds")

        # Framework-specific directories
        if self.config.framework == Framework.FASTAPI:
            directories.extend([
                "api/routes",
                "api/schemas",
            ])
        elif self.config.framework == Framework.FLASK:
            directories.extend([
                "app/routes",
                "app/templates",
                "app/static",
            ])

        for directory in directories:
            (self.config.path / directory).mkdir(parents=True, exist_ok=True)

    def _create_virtual_environment(self):
        """Create a virtual environment."""
        if not self.config.venv_path.exists():
            self._run_command(
                [self.python_cmd, "-m", "venv", str(self.config.venv_path)],
                cwd=self.config.path.parent
            )

    def _install_dependencies(self):
        """Install project dependencies."""
        dependencies = self.config.get_dependencies()

        python_exe = self._get_python_executable()

        # Upgrade pip
        self._run_command([python_exe, "-m", "pip", "install", "--upgrade", "pip"])

        # Install requirements
        self._run_command([python_exe, "-m", "pip", "install"] + dependencies)

        # Write requirements.txt
        self._write_file("requirements.txt", "\n".join(dependencies) + "\n")

    def _generate_files(self):
        """Generate all project files from templates."""
        # Core files
        self._write_file(".env", self._render_template("core/env.jinja2"))
        self._write_file(".gitignore", self._render_template("core/gitignore.jinja2"))
        self._write_file("__init__.py", "")
        self._write_file("data/__init__.py", "")
        self._write_file("data/db.py", self._render_template("database/db.py.jinja2"))

        # Docker (if included)
        if self.config.include_docker and self.config.database.requires_server:
            self._write_file(
                "docker-compose.yml",
                self._render_template("core/docker-compose.yml.jinja2")
            )

        # Models (base only)
        self._write_file("models/__init__.py", self._render_template("models/__init__.py.jinja2"))
        self._write_file("models/base.py", self._render_template("models/base.py.jinja2"))

        # Scripts
        self._write_file("scripts/__init__.py", "")

        if self.config.include_erd_generator:
            self._write_file(
                "scripts/generate_erd.py",
                self._render_template("scripts/generate_erd.py.jinja2")
            )

        if self.config.include_data_import:
            self._write_file(
                "scripts/data_import.py",
                self._render_template("scripts/data_import.py.jinja2")
            )
            # CSV import documentation
            self._write_file(
                "docs/CSV_IMPORT.md",
                self._render_template("docs/CSV_IMPORT.md.jinja2")
            )

        # Migrations
        self._write_file("migrations/__init__.py", "")

        # Tests
        if self.config.include_tests:
            self._write_file("tests/__init__.py", "")
            self._write_file("tests/conftest.py", self._render_template("tests/conftest.py.jinja2"))
            self._write_file(
                "tests/integration_tests/__init__.py",
                ""
            )
            self._write_file(
                "tests/integration_tests/test_database.py",
                self._render_template("tests/test_database.py.jinja2")
            )

        # Framework-specific files
        if self.config.framework == Framework.FASTAPI:
            self._generate_fastapi_files()
        elif self.config.framework == Framework.FLASK:
            self._generate_flask_files()
        else:
            self._generate_minimal_files()

    def _generate_fastapi_files(self):
        """Generate FastAPI-specific files."""
        self._write_file("main.py", self._render_template("frameworks/fastapi/main.py.jinja2"))
        self._write_file("api/__init__.py", "")
        self._write_file("api/routes/__init__.py", "")
        self._write_file("api/schemas/__init__.py", "")
        self._write_file(
            "api/routes/health.py",
            self._render_template("frameworks/fastapi/health.py.jinja2")
        )

    def _generate_flask_files(self):
        """Generate Flask-specific files."""
        self._write_file("app/__init__.py", self._render_template("frameworks/flask/app_init.py.jinja2"))
        self._write_file("app/routes/__init__.py", "")
        self._write_file(
            "app/routes/health.py",
            self._render_template("frameworks/flask/health.py.jinja2")
        )
        self._write_file("run.py", self._render_template("frameworks/flask/run.py.jinja2"))

    def _generate_minimal_files(self):
        """Generate minimal project files (no web framework)."""
        self._write_file("main.py", self._render_template("frameworks/minimal/main.py.jinja2"))

    def _initialize_alembic(self):
        """Initialize Alembic for database migrations."""
        # Write alembic.ini
        self._write_file("alembic.ini", self._render_template("migrations/alembic.ini.jinja2"))

        # Write env.py
        self._write_file("migrations/env.py", self._render_template("migrations/env.py.jinja2"))

        # Write script.py.mako
        self._write_file(
            "migrations/script.py.mako",
            self._render_template("migrations/script.py.mako.jinja2")
        )

    def _create_database(self):
        """Create the database."""
        python_exe = self._get_python_executable()

        if self.config.database == Database.POSTGRESQL:
            script = f'''
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="{self.config.db_user}",
        password="{self.config.db_password}",
        host="{self.config.db_host}",
        port="{self.config.db_port}"
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", ("{self.config.db_name}",))
    if not cur.fetchone():
        cur.execute('CREATE DATABASE "{self.config.db_name}"')
        print(f"Database '{self.config.db_name}' created successfully")
    else:
        print(f"Database '{self.config.db_name}' already exists")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Database creation failed: {{e}}")
    raise
'''
        elif self.config.database == Database.MYSQL:
            script = f'''
import pymysql

try:
    conn = pymysql.connect(
        host="{self.config.db_host}",
        port={self.config.db_port},
        user="{self.config.db_user}",
        password="{self.config.db_password}"
    )
    cur = conn.cursor()
    cur.execute("CREATE DATABASE IF NOT EXISTS `{self.config.db_name}`")
    print(f"Database '{self.config.db_name}' created successfully")
    cur.close()
    conn.close()
except Exception as e:
    print(f"Database creation failed: {{e}}")
    raise
'''
        else:
            # SQLite doesn't need database creation
            return

        self._run_command([python_exe, "-c", script])

    def _initialize_git(self):
        """Initialize a Git repository."""
        git_dir = self.config.path / ".git"
        if not git_dir.exists():
            self._run_command(["git", "init"])
            self._run_command(["git", "add", "."])
            self._run_command([
                "git", "commit", "-m",
                "Initial commit from create-sqlalchemy-app"
            ])
