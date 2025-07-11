"""Test Fixtures CLI - Generic tool for generating and managing test fixtures via API."""

__version__ = "0.1.0"

from .database import DatabaseConnector
from .generators.base import Generator
from .generators.example_generator import ExampleGenerator
from .generators.agent_generator import AgentGenerator
from .fixtures.example_fixtures import EXAMPLE_FIXTURES
from .fixtures.agent_fixtures import AGENT_FIXTURES

__all__ = [
    "DatabaseConnector",
    "Generator",
    "ExampleGenerator",
    "AgentGenerator",
    "EXAMPLE_FIXTURES",
    "AGENT_FIXTURES",
]