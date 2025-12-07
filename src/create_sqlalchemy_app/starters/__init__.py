"""
Starter Kits

Pre-built model collections that can be added to projects.

Available starters:
- auth: User model with authentication fields
- blog: User, Post, Comment, Tag models
- ecommerce: User, Product, Order, Category models

Usage:
    csa my-project --starter auth
    csa my-project --starter blog
    csa my-project --starter ecommerce
"""

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class StarterKit:
    """Definition of a starter kit."""

    name: str
    description: str
    models: List[str]  # List of model file names (without .py.jinja2)
    test_file: str  # Test file name (without .py.jinja2)

    @property
    def model_templates(self) -> Dict[str, str]:
        """Get mapping of template path to output path for models."""
        return {
            f"starters/{self.name}/models/{model}.py.jinja2": f"models/{model}.py"
            for model in self.models
        }

    @property
    def init_template(self) -> tuple:
        """Get the __init__.py template path and output path."""
        return (
            f"starters/{self.name}/models/__init__.py.jinja2",
            "models/__init__.py"
        )

    @property
    def test_template(self) -> tuple:
        """Get the test template path and output path."""
        return (
            f"starters/{self.name}/tests/{self.test_file}.py.jinja2",
            f"tests/integration_tests/{self.test_file}.py"
        )


# Starter kit registry
STARTERS = {
    "auth": StarterKit(
        name="auth",
        description="User model with authentication fields (email, password, status)",
        models=["user"],
        test_file="test_user",
    ),
    "blog": StarterKit(
        name="blog",
        description="Blog models: User, Post, Comment, Tag with relationships",
        models=["user", "post", "comment", "tag"],
        test_file="test_blog",
    ),
    "ecommerce": StarterKit(
        name="ecommerce",
        description="E-commerce models: User, Product, Order, OrderItem, Category",
        models=["user", "category", "product", "order"],
        test_file="test_ecommerce",
    ),
}


def get_starter(name: str) -> StarterKit:
    """Get a starter kit by name."""
    if name not in STARTERS:
        available = ", ".join(STARTERS.keys())
        raise ValueError(f"Unknown starter: {name}. Available: {available}")
    return STARTERS[name]


def list_starters() -> List[str]:
    """List available starter kits."""
    return list(STARTERS.keys())


def get_starter_descriptions() -> Dict[str, str]:
    """Get descriptions for all starter kits."""
    return {name: starter.description for name, starter in STARTERS.items()}
