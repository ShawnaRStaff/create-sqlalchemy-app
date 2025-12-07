"""
Tests for the configuration module.
"""

import pytest
from pathlib import Path

from create_sqlalchemy_app.config import ProjectConfig, Framework, Database


class TestProjectConfig:
    """Test ProjectConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ProjectConfig(
            name="test-project",
            path=Path("/tmp/test-project"),
        )

        assert config.name == "test-project"
        assert config.framework == Framework.MINIMAL
        assert config.database == Database.POSTGRESQL
        assert config.db_name == "mydb"
        assert config.db_user == "postgres"
        assert config.db_password == "postgres"
        assert config.db_host == "localhost"
        assert config.db_port == "5432"
        assert config.venv_name == ".venv"

    def test_venv_path(self):
        """Test virtual environment path calculation."""
        config = ProjectConfig(
            name="test-project",
            path=Path("/tmp/test-project"),
        )

        assert config.venv_path == Path("/tmp/test-project/.venv")

    def test_database_url_postgresql(self):
        """Test PostgreSQL database URL generation."""
        config = ProjectConfig(
            name="test",
            path=Path("/tmp/test"),
            database=Database.POSTGRESQL,
            db_name="testdb",
            db_user="user",
            db_password="pass",
            db_host="localhost",
            db_port="5432",
        )

        assert config.database_url == "postgresql://user:pass@localhost:5432/testdb"

    def test_database_url_sqlite(self):
        """Test SQLite database URL generation."""
        config = ProjectConfig(
            name="test",
            path=Path("/tmp/test"),
            database=Database.SQLITE,
            db_name="testdb",
        )

        assert config.database_url == "sqlite:///testdb.db"

    def test_database_url_mysql(self):
        """Test MySQL database URL generation."""
        config = ProjectConfig(
            name="test",
            path=Path("/tmp/test"),
            database=Database.MYSQL,
            db_name="testdb",
            db_user="user",
            db_password="pass",
            db_host="localhost",
            db_port="3306",
        )

        assert config.database_url == "mysql+pymysql://user:pass@localhost:3306/testdb"

    def test_get_dependencies_minimal(self):
        """Test dependency list for minimal framework."""
        config = ProjectConfig(
            name="test",
            path=Path("/tmp/test"),
            framework=Framework.MINIMAL,
            database=Database.SQLITE,
            include_tests=False,
            include_data_import=False,
        )

        deps = config.get_dependencies()

        assert "sqlalchemy>=2.0.0" in deps
        assert "alembic" in deps
        assert "python-dotenv" in deps
        # Should NOT include framework-specific deps
        assert "fastapi" not in deps
        assert "flask" not in deps

    def test_get_dependencies_fastapi(self):
        """Test dependency list for FastAPI framework."""
        config = ProjectConfig(
            name="test",
            path=Path("/tmp/test"),
            framework=Framework.FASTAPI,
            database=Database.POSTGRESQL,
            include_tests=True,
        )

        deps = config.get_dependencies()

        assert "fastapi" in deps
        assert "uvicorn[standard]" in deps
        assert "psycopg[binary]" in deps
        assert "pytest" in deps
        assert "pytest-asyncio" in deps

    def test_get_dependencies_flask(self):
        """Test dependency list for Flask framework."""
        config = ProjectConfig(
            name="test",
            path=Path("/tmp/test"),
            framework=Framework.FLASK,
            database=Database.MYSQL,
        )

        deps = config.get_dependencies()

        assert "flask" in deps
        assert "flask-sqlalchemy" in deps
        assert "pymysql" in deps

    def test_to_template_context(self):
        """Test template context generation."""
        config = ProjectConfig(
            name="test-project",
            path=Path("/tmp/test"),
            framework=Framework.FASTAPI,
            database=Database.POSTGRESQL,
        )

        context = config.to_template_context()

        assert context["project_name"] == "test-project"
        assert context["framework"] == "fastapi"
        assert context["database"] == "postgresql"
        assert context["is_fastapi"] is True
        assert context["is_flask"] is False
        assert context["is_minimal"] is False
        assert context["is_postgresql"] is True
        assert context["requires_server"] is True


class TestFrameworkEnum:
    """Test Framework enum."""

    def test_display_names(self):
        """Test display names for frameworks."""
        assert Framework.FASTAPI.display_name == "FastAPI"
        assert Framework.FLASK.display_name == "Flask"
        assert Framework.MINIMAL.display_name == "Minimal (no web framework)"

    def test_descriptions(self):
        """Test descriptions for frameworks."""
        assert "async" in Framework.FASTAPI.description.lower()
        assert "flexible" in Framework.FLASK.description.lower()
        assert "no web framework" in Framework.MINIMAL.description.lower()


class TestDatabaseEnum:
    """Test Database enum."""

    def test_display_names(self):
        """Test display names for databases."""
        assert Database.POSTGRESQL.display_name == "PostgreSQL"
        assert Database.SQLITE.display_name == "SQLite"
        assert Database.MYSQL.display_name == "MySQL/MariaDB"

    def test_drivers(self):
        """Test SQLAlchemy driver strings."""
        assert Database.POSTGRESQL.driver == "postgresql"
        assert Database.SQLITE.driver == "sqlite"
        assert Database.MYSQL.driver == "mysql+pymysql"
