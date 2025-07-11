# Generators Directory

This directory contains fixture **processing logic**. The actual data/configurations are in the `fixtures/` directory.

## What's Included

- **`base.py`** - Abstract base classes you should extend
- **`example_generator.py`** - Example generator logic (copy and modify this)
- **`example_database_generator.py`** - Example database operations (copy and modify this)
- **`.gitignore`** - Ignores your custom generators (keeps them private)

## Architecture Overview

```text
📁 fixtures/           <- Your data/configurations
   ├── example_fixtures.py    (fixture data)
   └── my_users.py         (your custom data)

📁 generators/         <- Processing logic
   ├── base.py             (base classes)
   ├── example_generator.py   (example generator)
   ├── example_database_generator.py         (database operations)
   └── my_user_generator.py (your custom logic)
```

## Creating Your Own Generator

### Step 1: Create Your Fixture Data

First, create your fixture data in the `fixtures/` directory:

```python
# fixtures/my_users.py
MY_USER_FIXTURES = {
    "admin": {
        "description": "Admin user",
        "config": {
            "username": "admin",
            "role": "admin"
        }
    }
}
```

### Step 2: Create Your Generator Logic

```python
# generators/my_user_generator.py
from .base import BaseFixtureGenerator
from ..fixtures.my_users import MY_USER_FIXTURES

class UserGenerator(BaseFixtureGenerator):
    def __init__(self):
        self.fixture_configs = MY_USER_FIXTURES

    def get_fixtures(self):
        fixtures = []
        for name, data in self.fixture_configs.items():
            config = data["config"].copy()
            config["fixture_id"] = name
            fixtures.append(config)
        return fixtures

    def list_available(self):
        return {name: config["description"]
                for name, config in self.fixture_configs.items()}
```

### Step 3: Create Database Operations

```python
# generators/my_user_database.py
from .base import BaseDatabaseGenerator
from .my_user_generator import UserGenerator

class UserDatabaseGenerator(BaseDatabaseGenerator):
    def __init__(self, api_url="http://localhost:3000"):
        super().__init__(api_url)
        self.fixture_generator = UserGenerator()

    def setup_fixtures(self, endpoint_template="/users/{fixture_id}/"):
        fixture_configs = self.fixture_generator.get_fixtures()
        created_fixtures = []

        for config in fixture_configs:
            fixture_id = config.pop("fixture_id")
            endpoint = endpoint_template.format(fixture_id=fixture_id)

            result = self.db.put(endpoint, json=config)

            created_fixture = config.copy()
            created_fixture["fixture_id"] = fixture_id
            created_fixtures.append(created_fixture)

        return created_fixtures

    def clear_fixtures(self, clear_endpoint="/users/"):
        return self.db.delete(clear_endpoint)

    def list_existing_fixtures(self, list_endpoint="/users/"):
        users = self.db.get(list_endpoint)
        return [user["id"] for user in users]  # Customize for your API
```

### Step 4: Use Your Generator

```python
from generators.my_user_database import UserDatabaseGenerator

generator = UserDatabaseGenerator("http://localhost:3000")
fixtures = generator.setup_fixtures("/users/{fixture_id}/")
print(f"Created {len(fixtures)} user fixtures")
```

## Key Benefits of This Structure

### 🎯 **Separation of Concerns**

- **Fixtures** = Data/configurations (what to create)
- **Generators** = Logic (how to process and create)

### 🔒 **Privacy Control**

- Fixture data can be kept private via `.gitignore`
- Generator logic can be shared/versioned
- Sensitive data (API keys) stays in fixtures

### 🔄 **Reusability**

```python
# Same generator logic, different data
user_gen = UserGenerator(MY_USER_FIXTURES)       # Dev data
prod_gen = UserGenerator(PRODUCTION_FIXTURES)    # Prod data
test_gen = UserGenerator(TEST_FIXTURES)          # Test data
```

### 🧩 **Modularity**

```python
# Mix and match different fixture sets
from fixtures.users import USER_FIXTURES
from fixtures.products import PRODUCT_FIXTURES

combined_fixtures = {**USER_FIXTURES, **PRODUCT_FIXTURES}
generator = MyGenerator(combined_fixtures)
```

## Generator Patterns

### Basic Generator

```python
class SimpleGenerator(BaseFixtureGenerator):
    def __init__(self, fixture_data):
        self.fixture_configs = fixture_data

    def get_fixtures(self):
        # Standard processing logic
        pass
```

### Environment-Aware Generator

```python
import os

class EnvironmentGenerator(BaseFixtureGenerator):
    def __init__(self):
        env = os.getenv("ENVIRONMENT", "dev")
        if env == "production":
            from ..fixtures.prod_data import PROD_FIXTURES
            self.fixture_configs = PROD_FIXTURES
        else:
            from ..fixtures.dev_data import DEV_FIXTURES
            self.fixture_configs = DEV_FIXTURES
```

### Multi-Type Generator

```python
class MultiTypeGenerator(BaseFixtureGenerator):
    def __init__(self):
        from ..fixtures.users import USER_FIXTURES
        from ..fixtures.products import PRODUCT_FIXTURES

        self.user_fixtures = USER_FIXTURES
        self.product_fixtures = PRODUCT_FIXTURES

    def get_fixtures(self, fixture_type="all"):
        if fixture_type == "users":
            return self._process_fixtures(self.user_fixtures)
        elif fixture_type == "products":
            return self._process_fixtures(self.product_fixtures)
        else:
            return (self._process_fixtures(self.user_fixtures) +
                   self._process_fixtures(self.product_fixtures))
```

### Validation Generator

```python
from pydantic import BaseModel

class User(BaseModel):
    username: str
    email: str
    role: str

class ValidatingGenerator(BaseFixtureGenerator):
    def get_fixtures(self):
        fixtures = []
        for name, data in self.fixture_configs.items():
            # Validate against Pydantic model
            user = User(**data["config"])

            config = user.dict()
            config["fixture_id"] = name
            fixtures.append(config)
        return fixtures
```

## Database Generator Patterns

### REST API Generator

```python
class RestApiGenerator(BaseDatabaseGenerator):
    def setup_fixtures(self, endpoint_template="/api/{fixture_id}/"):
        # PUT /api/user1/, PUT /api/admin/, etc.
        for config in self.fixture_generator.get_fixtures():
            fixture_id = config.pop("fixture_id")
            endpoint = endpoint_template.format(fixture_id=fixture_id)
            self.db.put(endpoint, json=config)
```

### Bulk API Generator

```python
class BulkApiGenerator(BaseDatabaseGenerator):
    def setup_fixtures(self, bulk_endpoint="/api/bulk/"):
        # POST /api/bulk/ with array of fixtures
        fixtures = self.fixture_generator.get_fixtures()
        self.db.post(bulk_endpoint, json={"fixtures": fixtures})
```

### GraphQL Generator

```python
class GraphQLGenerator(BaseDatabaseGenerator):
    def setup_fixtures(self, graphql_endpoint="/graphql"):
        for config in self.fixture_generator.get_fixtures():
            mutation = """
            mutation CreateUser($input: UserInput!) {
                createUser(input: $input) { id }
            }
            """
            self.db.post(graphql_endpoint, json={
                "query": mutation,
                "variables": {"input": config}
            })
```

## Testing Your Generators

```python
# test_my_generator.py
import pytest
from generators.my_user_generator import UserGenerator
from fixtures.my_users import MY_USER_FIXTURES

def test_user_generator():
    generator = UserGenerator()
    fixtures = generator.get_fixtures()

    assert len(fixtures) == len(MY_USER_FIXTURES)
    for fixture in fixtures:
        assert "fixture_id" in fixture
        assert "username" in fixture

def test_custom_fixture_data():
    custom_data = {
        "test_user": {
            "description": "Test user",
            "config": {"username": "test"}
        }
    }

    generator = UserGenerator()
    generator.fixture_configs = custom_data
    fixtures = generator.get_fixtures()

    assert len(fixtures) == 1
    assert fixtures[0]["username"] == "test"
```

## .gitignore Behavior

Files that are tracked:

- `base.py` (base classes)
- `example_agents.py` (example generator)
- `database.py` (example database operations)
- `README.md` (this file)

Files that are ignored:

- `my_*.py` (your custom generators)
- Any other `.py` files you create

## Tips

1. **Keep Logic Generic** - Make generators reusable with different fixture data
2. **Handle Errors Gracefully** - Add proper error handling for API failures
3. **Use Type Hints** - Help with IDE support and documentation
4. **Test Your Generators** - Unit test the processing logic
5. **Document API Requirements** - Note what endpoints your generator expects

## Example: Complete E-commerce Generator

```python
# generators/ecommerce_generator.py
from .base import BaseDatabaseGenerator
from ..fixtures.ecommerce import ECOMMERCE_FIXTURES

class EcommerceGenerator(BaseDatabaseGenerator):
    def __init__(self, api_url="http://localhost:4000"):
        super().__init__(api_url)
        from ..fixtures.ecommerce import ECOMMERCE_FIXTURES
        self.fixture_configs = ECOMMERCE_FIXTURES

    def setup_fixtures(self):
        # Create users first
        user_fixtures = {k: v for k, v in self.fixture_configs.items()
                        if v["config"].get("type") == "user"}
        self._create_fixtures(user_fixtures, "/users/{fixture_id}/")

        # Then products
        product_fixtures = {k: v for k, v in self.fixture_configs.items()
                           if v["config"].get("type") == "product"}
        self._create_fixtures(product_fixtures, "/products/{fixture_id}/")

        # Finally orders (depend on users/products)
        order_fixtures = {k: v for k, v in self.fixture_configs.items()
                         if v["config"].get("type") == "order"}
        self._create_fixtures(order_fixtures, "/orders/{fixture_id}/")

    def _create_fixtures(self, fixtures, endpoint_template):
        for name, data in fixtures.items():
            config = data["config"].copy()
            fixture_id = config.pop("fixture_id", name)
            endpoint = endpoint_template.format(fixture_id=fixture_id)
            self.db.put(endpoint, json=config)
```

Happy generating! 🚀
