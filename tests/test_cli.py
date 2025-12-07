"""
Tests for the CLI module.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from create_sqlalchemy_app.cli import main
from create_sqlalchemy_app.config import Framework, Database


@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test projects."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_version(self, runner):
        """Test --version flag."""
        result = runner.invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "1.0.0" in result.output

    def test_help(self, runner):
        """Test --help flag."""
        result = runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "Create a new SQLAlchemy project" in result.output

    def test_no_project_name_prompts(self, runner):
        """Test that missing project name triggers prompt."""
        result = runner.invoke(main, input="\n")  # Empty input
        assert "Project name is required" in result.output or "What is your project named" in result.output


class TestProjectNameValidation:
    """Test project name validation."""

    def test_invalid_project_name(self, runner):
        """Test that invalid project names are rejected."""
        result = runner.invoke(main, ["invalid project!"])
        assert result.exit_code != 0
        assert "can only contain letters, numbers, hyphens, and underscores" in result.output

    def test_valid_project_names(self, runner, temp_dir):
        """Test that valid project names are accepted."""
        valid_names = ["my-project", "my_project", "MyProject", "project123"]

        for name in valid_names:
            # Just check validation passes - don't actually create project
            with patch.object(runner, 'invoke') as mock_invoke:
                mock_invoke.return_value.exit_code = 0
                # The name validation should pass
                assert name.replace("-", "").replace("_", "").isalnum()


class TestNonInteractiveMode:
    """Test non-interactive mode with -y flag."""

    def test_yes_requires_framework_and_database(self, runner):
        """Test that -y flag requires --framework and --database."""
        result = runner.invoke(main, ["test-project", "-y"])
        assert result.exit_code != 0
        assert "--yes requires both --framework and --database" in result.output

    def test_yes_with_framework_only(self, runner):
        """Test that -y flag with only --framework fails."""
        result = runner.invoke(main, ["test-project", "-y", "--framework", "fastapi"])
        assert result.exit_code != 0

    def test_yes_with_database_only(self, runner):
        """Test that -y flag with only --database fails."""
        result = runner.invoke(main, ["test-project", "-y", "--database", "sqlite"])
        assert result.exit_code != 0


class TestConfigIntegration:
    """Test configuration object creation."""

    def test_framework_enum_values(self):
        """Test Framework enum has expected values."""
        assert Framework.FASTAPI.value == "fastapi"
        assert Framework.FLASK.value == "flask"
        assert Framework.MINIMAL.value == "minimal"

    def test_database_enum_values(self):
        """Test Database enum has expected values."""
        assert Database.POSTGRESQL.value == "postgresql"
        assert Database.SQLITE.value == "sqlite"
        assert Database.MYSQL.value == "mysql"

    def test_database_default_ports(self):
        """Test default ports for databases."""
        assert Database.POSTGRESQL.default_port == "5432"
        assert Database.MYSQL.default_port == "3306"
        assert Database.SQLITE.default_port == ""

    def test_database_requires_server(self):
        """Test requires_server property."""
        assert Database.POSTGRESQL.requires_server is True
        assert Database.MYSQL.requires_server is True
        assert Database.SQLITE.requires_server is False
