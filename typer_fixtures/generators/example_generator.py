"""Example fixture generator using unified Generator class."""

from .base import Generator


class ExampleGenerator(Generator):
    """Example fixture generator for demonstration."""

    def __init__(self, api_url: str = "http://localhost:8000", timeout: float = 30.0, fixture_data=None):
        """Initialize with example fixture data."""
        super().__init__(fixture_data, api_url, timeout)