"""
Blog Starter Kit

Provides models for a blog application:
- User: Blog authors
- Post: Blog posts with title, content, status
- Comment: Comments on posts
- Tag: Tags for categorizing posts (many-to-many)

Usage:
    csa my-project --starter blog
"""

STARTER_NAME = "blog"
STARTER_DESCRIPTION = "Blog models (User, Post, Comment, Tag)"

# Files to generate
FILES = [
    "models/user.py",
    "models/post.py",
    "models/comment.py",
    "models/tag.py",
    "tests/integration_tests/test_blog.py",
]
