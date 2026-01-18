"""Shared test fixtures for alertmanager-mcp tests."""

from typing import Any

import pytest
from pytest_mock import MockerFixture


@pytest.fixture
def mock_alertmanager_env(mocker: MockerFixture) -> Any:
    """Mock Alertmanager environment variables with defaults."""

    def mock_getenv(key: str, default: str | None = None) -> str | None:
        env_vars = {
            "ALERTMANAGER_URL": "http://fake-alertmanager",
            "ALERTMANAGER_TIMEOUT": "30",
            "ALERTMANAGER_USERNAME": None,
            "ALERTMANAGER_PASSWORD": None,
            "ALERTMANAGER_CREATED_BY": "alertmanager-mcp",
        }
        return env_vars.get(key, default)

    return mocker.patch("os.getenv", side_effect=mock_getenv)


@pytest.fixture
def mock_config(mock_alertmanager_env: Any) -> Any:
    """Create a mock Config instance with environment variables."""
    from alertmanager_mcp.config import Config

    return Config()


@pytest.fixture
def mock_client(mock_config: Any) -> Any:
    """Create a mock AlertmanagerClient instance."""
    from alertmanager_mcp.client import AlertmanagerClient

    return AlertmanagerClient(mock_config)
