# Test Fixtures CLI

A generic command-line tool for generating and managing test fixtures via API. Easily customizable for any API structure and data model.

## Features

- 🔧 **Unified Generator Architecture** - Single class handles both file and database operations
- 📦 **Automatic Fixture Discovery** - Generators automatically find their corresponding fixture files
- 🎯 **Naming Convention** - Simple rules for automatic pairing of generators and fixtures
- 🛡️ **Safety First** - Interactive confirmations for destructive operations
- 🚀 **Ready to Use** - Includes working examples
- 📝 **Multiple Formats** - JSON, Python, and YAML output
- 🔄 **Dynamic Discovery** - Automatically finds all available generators

## Architecture

```text
root/
├── typer_fixtures/
│   ├── database.py              # Generic HTTP client
│   ├── main.py                  # CLI application with dynamic discovery
│   ├── fixtures/                # 📁 Your data/configurations
│   │   ├── example_fixtures.py        (example fixture data)
│   │   ├── my_data_fixtures.py        (your custom data - private)
│   │   └── .gitignore              (keeps your data private)
│   └── generators/              # 📁 Processing logic
│       ├── base.py                 (unified generator base class)
│       ├── example_generator.py       (example generator)
│       ├── my_data_generator.py      (your custom logic - private)
│       └── .gitignore              (keeps your logic private)
```

## Naming Convention

The system uses a simple naming convention for automatic discovery:

- **Generator files**: Must end with `_generator.py`
- **Fixture files**: Must have same base name + `_fixtures.py`
- **Fixture variables**: Must end with `_FIXTURES`

### Examples

- `agent_generator.py` → `AgentGenerator` class → looks for `agent_fixtures.py` → loads `AGENT_FIXTURES`
- `example_generator.py` → `ExampleGenerator` class → looks for `example_fixtures.py` → loads `EXAMPLE_FIXTURES`

## Installation

```bash
cd typer-fixtures
poetry install
```

## Quick Start

### 1. Generate JSON Fixtures

```bash
# Generate all available fixtures
typer-fixtures generate

# Generate specific generator
typer-fixtures generate --generator example

# Save to file
typer-fixtures generate --save my_fixtures.json

# List available generators and fixtures
typer-fixtures generate --list-available
```

### 2. Database Operations

```bash
# Setup all generators (uses their own endpoints)
typer-fixtures database --setup

# Setup specific generator
typer-fixtures database --generator agent --setup

# List existing fixtures
typer-fixtures database --list-existing

# Reset everything (with confirmation)
typer-fixtures database --reset

# Reset and recreate (with confirmation)
typer-fixtures database --reset-and-setup

# Automation-friendly (skip confirmation)
typer-fixtures database --reset --confirm
```

## Customization Guide

### Creating Your Own Fixtures & Generators

#### Step 1: Create Your Fixture Data

```python
# fixtures/my_data_fixtures.py
from typing import Dict, Any

MY_DATA_FIXTURES: Dict[str, Dict[str, Any]] = {
    "admin": {
        "description": "Administrator user with full permissions",
        "config": {
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "permissions": ["read", "write", "delete"]
        }
    },
    "regular_user": {
        "description": "Regular user with limited permissions",
        "config": {
            "username": "user",
            "email": "user@example.com",
            "role": "user",
            "permissions": ["read"]
        }
    }
}
```

#### Step 2: Create Your Generator

```python
# generators/my_data_generator.py
from .base import Generator

class MyDataGenerator(Generator):
    def __init__(self, api_url="http://localhost:3000", timeout=30.0, fixture_data=None):
        # Fixtures are automatically discovered from my_data_fixtures.py if you don't pass fixture_data
        super().__init__(fixture_data, api_url, timeout)

        # Set your API endpoints
        self.default_create_endpoint = "/users/{fixture_id}/"
        self.default_list_endpoint = "/users/"
        self.default_clear_endpoint = "/users/"

    def list_existing_fixtures(self, list_endpoint=None):
        """Customize how to extract fixture IDs from your API response."""
        users = self.get_existing_fixtures(list_endpoint)
        return [user["id"] for user in users]
```

That's it! The generator will automatically:

1. Discover `my_data_fixtures.py` based on the class name
2. Load the `MY_DATA_FIXTURES` variable
3. Use the specified API endpoints

### Using the Generic Database Connector

The `DatabaseConnector` class provides standard HTTP methods:

```python
from app.database import DatabaseConnector

db = DatabaseConnector("http://localhost:3000")

# Standard HTTP methods
users = db.get("/users/")
user = db.post("/users/", json={"name": "John"})
updated = db.put("/users/123/", json={"name": "Jane"})
db.delete("/users/123/")

# Health checks
if db.health_check("/health"):
    print("API is ready!")
```

## Available Commands

### `generate`

Generate JSON fixtures using available generators:

```bash
typer-fixtures generate [OPTIONS]

Options:
  --format [json|python|yaml]  Output format
  --save TEXT                  Save to file
  --list-available            List all generators and fixtures
  --generator TEXT            Use specific generator only
```

### `database`

Manage fixtures in your database:

```bash
typer-fixtures database [OPTIONS]

Options:
  --api-url TEXT              API base URL
  --setup / --no-setup       Create fixtures (default)
  --reset                     Delete all fixtures (interactive confirmation)
  --reset-and-setup          Delete and recreate defaults (interactive confirmation)
  --confirm                   Skip interactive confirmation (for automation)
  --list-available           List all generators and fixtures
  --list-existing            List existing fixtures in database
  --generator TEXT            Use specific generator only
```

## Key Benefits

### 🎯 **Unified Architecture**

- **Single Generator Class** - Handles both file generation and database operations
- **Automatic Fixture Discovery** - No manual imports or configuration
- **Self-Contained Generators** - Each generator manages its own fixtures and endpoints

### 🔄 **Dynamic Discovery**

```bash
# Automatically finds all generators
typer-fixtures generate --list-available

# Output:
# Generator    Fixture    Description
# example      user       Example user fixture
# example      admin      Example admin fixture
# agent        default    Default agent configuration
# agent        service_guru Service guru agent configuration
```

### 🧩 **Easy Extension**

Just create two files following the naming convention:

```python
# generators/my_new_generator.py
class MyNewGenerator(Generator):
    def __init__(self, api_url="http://localhost:8000", timeout=30.0, fixture_data=None):
        super().__init__(fixture_data, api_url, timeout)
        self.default_create_endpoint = "/my-endpoint/{fixture_id}/"

# fixtures/my_new_fixtures.py
MY_NEW_FIXTURES = {
    "item1": {"description": "First item", "config": {"name": "Item 1"}}
}
```

The CLI automatically discovers and loads your new generator!

### 🛡️ **Safety Features**

- **Interactive confirmations** for destructive operations
- **Health checks** before operations
- **Comprehensive error handling** with helpful messages
- **Automation support** with `--confirm` flag
- **Graceful degradation** - broken generators don't crash the system

## Development Workflow

1. **Create fixture file** following naming convention (`my_data_fixtures.py`)
2. **Create generator file** following naming convention (`my_data_generator.py`)
3. **Define your fixtures** with descriptions and configurations
4. **Set your API endpoints** in the generator constructor
5. **Test locally** - the CLI automatically discovers your new generator
6. **Keep sensitive data private** - it's automatically gitignored

## Contributing

This is designed to be a template. Fork it, customize it, make it your own! The unified architecture makes it easy to:

- Add new generators (just follow the naming convention)
- Support different API patterns (each generator defines its own endpoints)
- Extend with new output formats
- Add custom validation logic
- Keep your customizations private

## License

Feel free to use this as a starting point for your own fixture management tools.

---

**Ready to customize?**

1. Create `fixtures/my_data_fixtures.py` with your fixture data
2. Create `generators/my_data_generator.py` with your generator logic
3. Follow the naming convention for automatic discovery
4. Your customizations will be automatically gitignored and stay private!
