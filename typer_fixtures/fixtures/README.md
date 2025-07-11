# Fixtures Directory

This directory contains your fixture **data/configurations**. This is separate from generators (which contain the processing logic).

## What's Here

- **`example_agents.py`** - Example fixture data for agents (you can copy and modify)
- **`.gitignore`** - Keeps your custom fixtures private

## Creating Your Own Fixtures

### Step 1: Copy the Example

```bash
cp example_agents.py my_users.py
```

### Step 2: Define Your Fixture Data

```python
# my_users.py
from typing import Dict, Any

MY_USER_FIXTURES: Dict[str, Dict[str, Any]] = {
    "admin": {
        "description": "Administrator user with full permissions",
        "config": {
            "username": "admin",
            "email": "admin@example.com",
            "role": "admin",
            "permissions": ["read", "write", "delete"],
            "active": True
        }
    },
    "regular_user": {
        "description": "Regular user with limited permissions",
        "config": {
            "username": "user",
            "email": "user@example.com",
            "role": "user", 
            "permissions": ["read"],
            "active": True
        }
    },
    "inactive_user": {
        "description": "Inactive user for testing deactivation",
        "config": {
            "username": "inactive",
            "email": "inactive@example.com",
            "role": "user",
            "permissions": [],
            "active": False
        }
    }
}

# You can also define environment-specific fixtures
PRODUCTION_USER_FIXTURES: Dict[str, Dict[str, Any]] = {
    "admin": {
        "description": "Production admin - limited access",
        "config": {
            "username": "prod_admin",
            "email": "admin@company.com",
            "role": "admin",
            "permissions": ["read", "write"],  # No delete in prod!
            "active": True
        }
    }
}
```

### Step 3: Use in Your Generator

```python
# generators/my_user_generator.py
from .base import BaseFixtureGenerator
from ..fixtures.my_users import MY_USER_FIXTURES

class UserGenerator(BaseFixtureGenerator):
    def __init__(self):
        self.fixture_configs = MY_USER_FIXTURES
    
    def get_fixtures(self):
        # Generator logic here...
        pass
```

## Fixture Data Structure

Each fixture should follow this pattern:

```python
FIXTURE_NAME: Dict[str, Dict[str, Any]] = {
    "fixture_id": {
        "description": "Human-readable description",
        "config": {
            # Your actual data that gets sent to the API
            "field1": "value1",
            "field2": "value2",
            # ... any structure your API expects
        }
    }
}
```

## Best Practices

### 1. **Descriptive Names**

```python
# Good
"admin_with_full_permissions": {...}
"readonly_user": {...}
"expired_subscription_user": {...}

# Avoid
"user1": {...}
"test": {...}
```

### 2. **Clear Descriptions**

```python
"admin": {
    "description": "Administrator with user management and system config access",
    "config": {...}
}
```

### 3. **Environment-Specific Data**

```python
import os

# Load different fixtures based on environment
ENVIRONMENT = os.getenv("ENV", "dev")

if ENVIRONMENT == "production":
    USER_FIXTURES = PRODUCTION_FIXTURES
elif ENVIRONMENT == "staging":
    USER_FIXTURES = STAGING_FIXTURES
else:
    USER_FIXTURES = DEVELOPMENT_FIXTURES
```

### 4. **Modular Organization**

```python
# For large datasets, split by category
USER_FIXTURES = {...}
PRODUCT_FIXTURES = {...}
ORDER_FIXTURES = {...}

# Or combine them
ALL_FIXTURES = {
    **USER_FIXTURES,
    **PRODUCT_FIXTURES,
    **ORDER_FIXTURES
}
```

## Common Patterns

### API Key Management

```python
import os

API_FIXTURES = {
    "service_a": {
        "description": "Service A configuration",
        "config": {
            "api_key": os.getenv("SERVICE_A_API_KEY", "test-key"),
            "endpoint": "https://api.service-a.com",
            "timeout": 30
        }
    }
}
```

### Database Connection Strings

```python
DATABASE_FIXTURES = {
    "primary_db": {
        "description": "Primary database connection",
        "config": {
            "host": os.getenv("DB_HOST", "localhost"),
            "port": int(os.getenv("DB_PORT", "5432")),
            "database": os.getenv("DB_NAME", "testdb"),
            "username": os.getenv("DB_USER", "testuser"),
            "password": os.getenv("DB_PASS", "testpass")
        }
    }
}
```

### Test Data with Relationships

```python
USER_FIXTURES = {
    "team_lead": {
        "description": "Team lead with direct reports",
        "config": {
            "id": 1,
            "username": "team_lead",
            "role": "manager",
            "team_members": [2, 3, 4]  # References to other fixtures
        }
    },
    "developer_1": {
        "description": "Senior developer",
        "config": {
            "id": 2,
            "username": "dev1",
            "role": "developer",
            "manager_id": 1  # References team_lead
        }
    }
}
```

## Privacy & .gitignore

The `.gitignore` in this directory ensures:

- ✅ Your custom fixtures stay private
- ✅ Example fixtures are shared in the repo
- ✅ API keys and sensitive data don't leak
- ✅ You can safely commit changes to examples

Files that are tracked:

- `example_agents.py` (example data)
- `__init__.py` (package file)
- `README.md` (this file)

Files that are ignored:

- `my_*.py` (your custom fixtures)
- Any other `.py` files you create

## Tips

1. **Keep Sensitive Data Out** - Use environment variables for API keys, passwords, etc.
2. **Use Realistic Data** - Make your test data close to real data for better testing
3. **Document Edge Cases** - Include fixtures for error conditions, edge cases
4. **Version Control** - Consider versioning your fixture data for different releases
5. **Validate Structure** - Consider adding type hints or Pydantic models

## Example: Complete E-commerce Fixtures

```python
# ecommerce_fixtures.py
ECOMMERCE_FIXTURES = {
    # Users
    "customer": {
        "description": "Regular customer with purchase history",
        "config": {
            "type": "user",
            "email": "customer@example.com",
            "subscription": "premium",
            "orders": 5
        }
    },
    
    # Products  
    "bestseller_product": {
        "description": "Popular product with high sales",
        "config": {
            "type": "product",
            "name": "Bestselling Widget",
            "price": 29.99,
            "stock": 100,
            "category": "widgets"
        }
    },
    
    # Orders
    "recent_order": {
        "description": "Recent order for testing fulfillment",
        "config": {
            "type": "order",
            "customer_id": "customer",
            "products": ["bestseller_product"],
            "status": "pending",
            "total": 29.99
        }
    }
}
```

Happy fixture creating! 🎯
