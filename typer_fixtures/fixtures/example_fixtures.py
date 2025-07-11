"""Example fixture data - copy and modify for your own domain."""

from typing import Dict, Any

EXAMPLE_FIXTURES: Dict[str, Dict[str, Any]] = {
    "user_example": {
        "description": "An example user fixture showing proper data wrapper structure",
        "data": {
            "user_example": {
                "username": "example_user",
                "email": "user@example.com",
                "role": "user",
                "active": True,
                "permissions": ["read", "write"]
            }
        }
    },
    "admin_example": {
        "description": "An example admin fixture with nested configuration",
        "data": {
            "admin_example": {
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin",
                "active": True,
                "permissions": ["read", "write", "delete", "manage_users"],
                "settings": {
                    "theme": "dark",
                    "notifications": True,
                    "timezone": "UTC"
                }
            }
        }
    }
}

# Example: Users can add their own fixture data, just make sure it ends with _FIXTURES.
# You can have multiple fixture variables in the same file and they will all be loaded.

# MY_CUSTOM_FIXTURES = {
#     "admin_user": {
#         "description": "Administrator user with full permissions",
#         "data": {
#             "admin_user": {
#                 "username": "admin",
#                 "email": "admin@example.com",
#                 "role": "admin",
#                 "permissions": ["read", "write", "delete"]
#             }
#         }
#     },
#     "regular_user": {
#         "description": "Regular user with limited permissions",
#         "data": {
#             "regular_user": {
#                 "username": "user",
#                 "email": "user@example.com",
#                 "role": "user",
#                 "permissions": ["read"]
#             }
#         }
#     }
# }

# PRODUCTION_FIXTURES = {
#     "prod_admin": {
#         "description": "Production admin with restricted access",
#         "data": {
#             "prod_admin": {
#                 "username": "prod_admin",
#                 "email": "admin@company.com",
#                 "role": "admin",
#                 "permissions": ["read", "write"],  # No delete in production!
#                 "environment": "production"
#             }
#         }
#     }
# }