"""Unified base class for fixture generators."""

import json
import os
import importlib
from abc import ABC
from typing import Dict, List, Any, Optional

from ..database import DatabaseConnector


class Generator:
    """Unified generator for fixtures with file and database operations."""

    def __init__(self, fixture_data: Optional[Dict[str, Dict[str, Any]]] = None, api_url: str = "http://localhost:8000", timeout: float = 30.0):
        """
        Initialize generator with fixture data and optional database connection.

        Args:
            fixture_data: Dictionary of fixture configurations
            api_url: Base URL of the API for database operations
            timeout: Request timeout in seconds
        """
        self.db = DatabaseConnector(api_url, timeout) if api_url else None

        self.default_create_endpoint = "/{fixture_id}/"
        self.default_list_endpoint = "/"
        self.default_clear_endpoint = "/"

        if fixture_data is None:
            fixture_data = self._discover_fixtures()

        self.fixture_configs = fixture_data or {}

    def _discover_fixtures(self) -> Optional[Dict[str, Dict[str, Any]]]:
        """
        Automatically discover and load fixtures based on generator class name.

        Looks for a fixture file with the same base name as the generator class.
        For example, AgentGenerator looks for agent_fixtures.py and loads all *_FIXTURES variables.

        Returns:
            Merged fixture data dictionary or None if not found
        """
        class_name = self.__class__.__name__
        if class_name.endswith('Generator'):
            base_name = class_name[:-9].lower()
        else:
            base_name = class_name.lower()

        fixture_module_name = f"{base_name}_fixtures"

        current_dir = os.path.dirname(os.path.abspath(__file__))
        fixtures_dir = os.path.join(current_dir, "..", "fixtures")
        fixture_file_path = os.path.join(fixtures_dir, f"{fixture_module_name}.py")

        if not os.path.exists(fixture_file_path):
            return None

        try:
            fixture_module = importlib.import_module(f"typer_fixtures.fixtures.{fixture_module_name}")

            # collect all *_FIXTURES variables and merge them
            merged_fixtures = {}
            fixtures_found = []

            for attr_name in dir(fixture_module):
                if attr_name.endswith('_FIXTURES'):
                    fixture_data = getattr(fixture_module, attr_name)
                    if isinstance(fixture_data, dict):
                        merged_fixtures.update(fixture_data)
                        fixtures_found.append(attr_name)

            if fixtures_found:
                print(f"Loaded fixtures from {fixture_module_name}: {', '.join(fixtures_found)}")
                return merged_fixtures

            return None

        except Exception as e:
            print(f"Warning: Could not load fixtures from {fixture_module_name}: {e}")
            return None

    def get_fixtures(self) -> List[Dict[str, Any]]:
        """Generate and return fixture data."""
        fixtures = []

        for fixture_name, fixture_data in self.fixture_configs.items():
            if 'data' in fixture_data:
                data = fixture_data["data"].copy()
            else:
                # For simple fixtures that don't have the data wrapper
                metadata_keys = ['description', 'tags']
                data = {k: v for k, v in fixture_data.items() if k not in metadata_keys}

            data["fixture_id"] = fixture_name
            fixtures.append(data)

        return fixtures

    def get_fixture_by_name(self, name: str) -> Dict[str, Any]:
        """Get a specific fixture configuration by name."""
        if name not in self.fixture_configs:
            raise ValueError(f"Fixture '{name}' not found. Available: {list(self.fixture_configs.keys())}")

        fixture_data = self.fixture_configs[name]
        if 'data' in fixture_data:
            data = fixture_data["data"].copy()
        else:
            metadata_keys = ['description', 'tags']
            data = {k: v for k, v in fixture_data.items() if k not in metadata_keys}

        data["fixture_id"] = name
        return data

    def list_available(self) -> Dict[str, str]:
        """Return available fixture types and their descriptions."""
        result = {}
        for name, config in self.fixture_configs.items():
            if 'description' in config:
                result[name] = config["description"]
            else:
                result[name] = f"Fixture: {name}"
        return result

    def add_fixture(self, name: str, description: str, config: Dict[str, Any]) -> None:
        """Add a new fixture configuration."""
        self.fixture_configs[name] = {
            "description": description,
            "config": config
        }

    def save_to_files(self, output_dir: str = "fixtures", filename: str = "fixtures.json") -> str:
        """
        Save fixtures to JSON file.

        Args:
            output_dir: Directory to save files in
            filename: Name of the output file

        Returns:
            Path to the saved file
        """
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)

        fixtures = self.get_fixtures()
        with open(filepath, 'w') as f:
            json.dump(fixtures, f, indent=2)

        return filepath

    def load_from_file(self, filepath: str) -> None:
        """
        Load fixtures from JSON file.

        Args:
            filepath: Path to the JSON file
        """
        with open(filepath, 'r') as f:
            fixtures = json.load(f)

        self.fixture_configs = {}
        for fixture in fixtures:
            fixture_id = fixture.pop("fixture_id")
            self.fixture_configs[fixture_id] = {"config": fixture}

    # database operations are only available if db is configured
    def health_check(self, endpoint: str = "/", max_retries: int = 30, delay: float = 1.0) -> bool:
        """Check if the API is ready."""
        if not self.db:
            raise ValueError("Database not configured. Set api_url in constructor.")
        return self.db.health_check(endpoint, max_retries, delay)

    def create_fixture_in_database(self, fixture_config: Dict[str, Any], endpoint_template: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a single fixture in the database via API call.

        Args:
            fixture_config: Fixture configuration dictionary
            endpoint_template: API endpoint template (defaults to self.default_create_endpoint)
        """
        if not self.db:
            raise ValueError("Database not configured. Set api_url in constructor.")

        endpoint_template = endpoint_template or self.default_create_endpoint
        fixture_id = fixture_config.pop("fixture_id")
        endpoint = endpoint_template.format(fixture_id=fixture_id)

        try:
            result = self.db.put(endpoint, json=fixture_config)

            # Return the created fixture info
            created_fixture = fixture_config.copy()
            created_fixture["fixture_id"] = fixture_id
            return created_fixture

        except Exception as e:
            raise Exception(f"Failed to create fixture {fixture_id}: {e}")

    def setup_fixtures(self, endpoint_template: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Create fixtures in the database.

        Args:
            endpoint_template: API endpoint template for creating fixtures
        """
        if not self.fixture_configs:
            raise ValueError("No fixture data configured.")

        endpoint_template = endpoint_template or self.default_create_endpoint
        fixture_configs = self.get_fixtures()

        created_fixtures = []
        for config in fixture_configs:
            try:
                created_fixture = self.create_fixture_in_database(config, endpoint_template)
                created_fixtures.append(created_fixture)

            except Exception as e:
                print(f"Warning: Failed to create fixture {config.get('fixture_id', 'unknown')}: {e}")
                continue

        return created_fixtures

    def get_existing_fixtures(self, list_endpoint: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get list of existing fixtures from the API.

        Args:
            list_endpoint: API endpoint for listing fixtures
        """
        if not self.db:
            raise ValueError("Database not configured. Set api_url in constructor.")

        list_endpoint = list_endpoint or self.default_list_endpoint
        try:
            return self.db.get(list_endpoint)
        except Exception as e:
            raise Exception(f"Failed to get existing fixtures: {e}")

    def clear_fixtures(self, clear_endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Clear all fixtures from the database.

        Args:
            clear_endpoint: API endpoint for clearing all fixtures
        """
        if not self.db:
            raise ValueError("Database not configured. Set api_url in constructor.")

        clear_endpoint = clear_endpoint or self.default_clear_endpoint
        try:
            result = self.db.delete(clear_endpoint)
            return result
        except Exception as e:
            raise Exception(f"Failed to clear fixtures: {e}")

    def list_existing_fixtures(self, list_endpoint: Optional[str] = None) -> List[str]:
        """
        List existing fixture IDs from the database.

        Override this method to customize how fixture IDs are extracted from your API response.

        Args:
            list_endpoint: API endpoint for listing fixtures
        """
        try:
            fixtures = self.get_existing_fixtures(list_endpoint)

            #  verride this if your API has a different structure
            if isinstance(fixtures, list) and fixtures:
                first_item = fixtures[0]

                # common patterns
                if isinstance(first_item, str):
                    return fixtures
                elif isinstance(first_item, dict):
                    # common ID field names
                    for id_field in ['id', 'fixture_id', 'name']:
                        if id_field in first_item:
                            return [item[id_field] for item in fixtures]

                    # no common field, returning the keys
                    return [str(i) for i in range(len(fixtures))]

            return []

        except Exception as e:
            raise Exception(f"Failed to list existing fixtures: {e}")

    def reset_fixtures(self, confirm: bool = False, clear_endpoint: Optional[str] = None, list_endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Reset all fixtures in the database.

        Args:
            confirm: Whether to skip confirmation (for automation)
            clear_endpoint: API endpoint for clearing all fixtures
            list_endpoint: API endpoint for listing fixtures
        """
        try:
            existing_fixtures = self.list_existing_fixtures(list_endpoint)
            result_data = self.clear_fixtures(clear_endpoint)

            return {
                "message": f"Reset completed - deleted {result_data.get('count', len(existing_fixtures))} fixtures",
                "fixtures_deleted": existing_fixtures,
                "count": result_data.get('count', len(existing_fixtures)),
                "status": "completed"
            }

        except Exception as e:
            if "405" in str(e):
                return {
                    "message": f"Reset skipped - no fixtures were deleted because the method is not allowed. {e}",
                    "fixtures_deleted": [],
                    "count": 0,
                    "status": "warning"
                }
            raise Exception(f"Failed to reset fixtures: {e}")

    def reset_and_setup(self, confirm: bool = False, clear_endpoint: Optional[str] = None, list_endpoint: Optional[str] = None, setup_endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Reset all fixtures and recreate defaults.

        Args:
            confirm: Whether to skip confirmation (for automation)
            clear_endpoint: API endpoint for clearing all fixtures
            list_endpoint: API endpoint for listing fixtures
            setup_endpoint: API endpoint template for creating fixtures
        """
        reset_result = self.reset_fixtures(confirm=True, clear_endpoint=clear_endpoint, list_endpoint=list_endpoint)
        if reset_result["status"] == "warning":
            return {
                "reset": reset_result,
                "created_fixtures": [],
                "status": "warning"
            }

        created_fixtures = self.setup_fixtures(setup_endpoint)

        return {
            "reset": reset_result,
            "created_fixtures": created_fixtures,
            "status": "completed"
        }