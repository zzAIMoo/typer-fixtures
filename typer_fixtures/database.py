"""Generic database/API connector for fixture management."""

import time
from typing import Dict, List, Any, Optional, Union
import httpx


class DatabaseConnector:
    """Generic API client for database operations."""

    def __init__(self, api_url: str = "http://localhost:8000", timeout: float = 30.0):
        self.api_url = api_url.rstrip('/')
        self.timeout = httpx.Timeout(timeout)

    def health_check(self, endpoint: str = "/", max_retries: int = 30, delay: float = 1.0) -> bool:
        """Check if the API is ready and responsive."""
        for attempt in range(max_retries):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.get(f"{self.api_url}{endpoint}")
                    if response.status_code == 200:
                        return True
            except (httpx.RequestError, httpx.TimeoutException):
                if attempt < max_retries - 1:
                    time.sleep(delay)
                continue
        return False

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a GET request to the API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.get(f"{self.api_url}{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"GET request failed for {endpoint}: {e}")

    def post(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a POST request to the API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(f"{self.api_url}{endpoint}", data=data, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"POST request failed for {endpoint}: {e}")

    def put(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a PUT request to the API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.put(f"{self.api_url}{endpoint}", data=data, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"PUT request failed for {endpoint}: {e}")

    def delete(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a DELETE request to the API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.delete(f"{self.api_url}{endpoint}", params=params)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"DELETE request failed for {endpoint}: {e}")

    def patch(self, endpoint: str, data: Optional[Dict] = None, json: Optional[Dict] = None) -> Dict[str, Any]:
        """Make a PATCH request to the API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.patch(f"{self.api_url}{endpoint}", data=data, json=json)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"PATCH request failed for {endpoint}: {e}")

    def request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Make a custom request to the API."""
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.request(method, f"{self.api_url}{endpoint}", **kwargs)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPError as e:
            raise Exception(f"{method.upper()} request failed for {endpoint}: {e}") 