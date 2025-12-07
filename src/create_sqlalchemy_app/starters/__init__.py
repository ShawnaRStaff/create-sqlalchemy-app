"""
Starter Kits

Pre-built model collections that can be added to projects.

Available starters (coming soon):
- auth: User model with authentication fields
- blog: User, Post, Comment, Tag models
- ecommerce: User, Product, Order, Category models

Usage:
    csa my-project --starter auth
"""

# Starter kit registry
STARTERS = {
    # "auth": AuthStarter,
    # "blog": BlogStarter,
    # "ecommerce": EcommerceStarter,
}


def get_starter(name: str):
    """Get a starter kit by name."""
    if name not in STARTERS:
        available = ", ".join(STARTERS.keys()) or "none yet"
        raise ValueError(f"Unknown starter: {name}. Available: {available}")
    return STARTERS[name]


def list_starters() -> list:
    """List available starter kits."""
    return list(STARTERS.keys())
