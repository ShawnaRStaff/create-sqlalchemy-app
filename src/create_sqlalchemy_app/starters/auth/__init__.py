"""
Auth Starter Kit

Provides a User model with authentication fields:
- id (UUID)
- email (unique)
- username (unique)
- password_hash
- is_active
- is_verified
- created_at
- updated_at

Usage:
    csa my-project --starter auth
"""

STARTER_NAME = "auth"
STARTER_DESCRIPTION = "User model with authentication fields"

# Files to generate
FILES = [
    "models/user.py",
    "tests/integration_tests/test_user.py",
]
