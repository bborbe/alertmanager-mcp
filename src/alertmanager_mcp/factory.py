"""Factory functions for creating Alertmanager MCP components."""

import logging

from .client import AlertmanagerClient
from .config import get_config

logger = logging.getLogger(__name__)

# Singleton client instance
_client: AlertmanagerClient | None = None


def get_client() -> AlertmanagerClient:
    """Get or create the Alertmanager client singleton.

    This function implements lazy initialization of the AlertmanagerClient.
    The client is created on first access and reused for subsequent calls.

    Returns:
        AlertmanagerClient: The singleton Alertmanager client instance.

    Example:
        >>> client = get_client()
        >>> alerts = client.get_alerts()
        >>> len(alerts)
        5
    """
    global _client
    if _client is None:
        logger.debug("Initializing Alertmanager client")
        _client = AlertmanagerClient(get_config())
    return _client
