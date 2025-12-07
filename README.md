# Create SQLAlchemy App

Create SQLAlchemy applications with a single command - like Create React App, but for Python backends.

```bash
pip install create-sqlalchemy-app
csa my-project
```

## Installation

### Windows
```bash
pip install create-sqlalchemy-app
```

### macOS (Homebrew Python)
```bash
brew install pipx
pipx install create-sqlalchemy-app
```

### Linux
```bash
pip install create-sqlalchemy-app
# or with pipx:
pipx install create-sqlalchemy-app
```

After installation, both `create-sqlalchemy-app` and `csa` commands are available.

## Features

- **Zero Configuration**: Get started immediately with sensible defaults
- **Multiple Frameworks**: Choose FastAPI, Flask, or minimal (no framework)
- **Multiple Databases**: PostgreSQL, SQLite, or MySQL support
- **Alembic Migrations**: Database versioning out of the box
- **Docker Ready**: Optional Docker Compose setup for databases
- **Testing Infrastructure**: Pre-configured pytest with production DB
- **ERD Generator**: Auto-generate database diagrams (only when schema changes)
- **CSV Import**: Framework for importing data from CSV files
- **Beautiful CLI**: Interactive prompts with rich output
- **Starter Kits**: Pre-built models for auth, blog, and e-commerce projects

## Quick Start

### Create a New Project

Interactive mode (recommended):
```bash
create-sqlalchemy-app my-project
# or use the short alias:
csa my-project
```

Non-interactive with all options:
```bash
csa my-project \
  --framework fastapi \
  --database postgresql \
  --db-name mydb \
  --db-user postgres \
  --db-password secret \
  -y
```

### What's Generated

```
my-project/
├── .venv/                # Virtual environment
├── models/               # SQLAlchemy models
│   ├── __init__.py
│   └── base.py           # Base class with documentation
├── migrations/           # Alembic migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
├── scripts/
│   ├── generate_erd.py   # ERD diagram generator
│   └── data_import.py    # CSV data importer
├── tests/
│   ├── conftest.py       # Test fixtures
│   └── integration_tests/
├── data/
│   └── db.py             # Database configuration
├── docs/
│   └── CSV_IMPORT.md     # CSV import guide
├── .env                  # Environment variables
├── .gitignore
├── alembic.ini
├── requirements.txt
└── docker-compose.yml    # (if Docker selected)
```

**Framework-specific files:**
- FastAPI: `main.py`, `api/routes/`
- Flask: `app/`, `run.py`
- Minimal: `main.py` (just database operations)

## CLI Options

```
Usage: create-sqlalchemy-app [OPTIONS] [PROJECT_NAME]

Options:
  -d, --directory PATH    Parent directory for the project
  -f, --framework         Framework: fastapi, flask, minimal
  -db, --database         Database: postgresql, sqlite, mysql
  --db-name TEXT          Database name
  --db-user TEXT          Database user
  --db-password TEXT      Database password
  --db-host TEXT          Database host (default: localhost)
  --db-port TEXT          Database port
  --no-docker             Skip Docker setup
  --no-tests              Skip test suite
  --no-git                Skip Git initialization
  --no-erd                Skip ERD generator
  --no-csv-import         Skip CSV import module
  -s, --starter           Starter kit: auth, blog, ecommerce
  -y, --yes               Skip prompts (requires --framework and --database)
  --version               Show version and exit
  --help                  Show this message and exit
```

## After Creating Your Project

1. **Navigate to your project:**
   ```bash
   cd my-project
   ```

2. **Start the database (if using Docker):**
   ```bash
   docker-compose up -d
   ```

3. **Activate the virtual environment:**
   ```bash
   # Unix/macOS
   source .venv/bin/activate

   # Windows
   .\.venv\Scripts\activate
   ```

4. **Create your models** in `models/` directory (see `models/base.py` for examples)

5. **Create and apply migrations:**
   ```bash
   alembic revision --autogenerate -m "Initial migration"
   alembic upgrade head
   ```

6. **Run your application:**
   ```bash
   # FastAPI
   uvicorn main:app --reload

   # Flask
   python run.py

   # Minimal
   python main.py
   ```

7. **Run tests:**
   ```bash
   pytest -xvs
   ```

## Creating Models

The generated `models/base.py` includes comprehensive documentation. Here's a quick example:

```python
# models/user.py
from sqlalchemy import Column, String, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
import uuid
from .base import Base

class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    username = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
```

Don't forget to add it to `models/__init__.py`:
```python
from .base import Base
from .user import User

__all__ = ["Base", "User"]
```

## CSV Data Import

The generated `scripts/data_import.py` provides a framework for importing CSV data. **Important**: You must create models and configure the script before importing.

See `docs/CSV_IMPORT.md` for detailed instructions.

## ERD Generation

Generate database diagrams:

```bash
python scripts/generate_erd.py
```

The ERD is only regenerated when the schema changes (hash-based detection). Use `--force` to regenerate anyway.

## Database Options

| Database       | Best For                                  |
|----------------|-------------------------------------------|
| **PostgreSQL** | Production, full-featured, recommended    |
| **SQLite**     | Development, prototyping, simple projects |
| **MySQL**      | Legacy systems, shared hosting            |

## Framework Comparison

| Framework   | Best For                                
|
|-------------|-----------------------------------------|
| **FastAPI** | Modern APIs, async, auto-documentation  |
| **Flask**   | Traditional web apps, flexibility       |
| **Minimal** | ETL, scripts, data processing, learning |

## Testing

Tests use the **same database type** as production (not SQLite for everything). This ensures tests accurately reflect production behavior.

A separate test database (`{db_name}_test`) is created automatically.

## Development

Clone and install in development mode:

```bash
git clone https://github.com/ShawnaRStaff/create-sqlalchemy-app.git
cd create-sqlalchemy-app
pip install -e ".[dev]"
```

Run package tests:
```bash
pytest tests/
```

## Starter Kits

Skip the boilerplate with pre-built models:

```bash
csa my-project --starter auth        # User model with authentication
csa my-project --starter blog        # User, Post, Comment, Tag models
csa my-project --starter ecommerce   # User, Product, Order, Category models
```

Each starter includes models with relationships and matching tests.

## Roadmap

- [x] Starter kits (auth, blog, ecommerce)
- [ ] API schema generation (Pydantic models)
- [ ] Authentication boilerplate (JWT/sessions)
- [ ] Deployment configurations (Docker, cloud)

## License

MIT License - see LICENSE for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

- Email: shawnastaff@gmail.com
- GitHub: [ShawnaRStaff](https://github.com/ShawnaRStaff)
