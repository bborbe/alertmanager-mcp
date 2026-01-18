import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


class Config:
    """
    Configuration class for the Alertmanager MCP server.
    Loads settings from environment variables.

    Environment variables:
        ALERTMANAGER_URL (required): URL of the Alertmanager instance
        ALERTMANAGER_USERNAME (optional): Username for HTTP basic auth
        ALERTMANAGER_PASSWORD (optional): Password for HTTP basic auth
        ALERTMANAGER_TIMEOUT (optional): Request timeout in seconds (default: 30)
        ALERTMANAGER_CREATED_BY (optional): Identity for silence creation
            (default: alertmanager-mcp)

    Note: Authentication is optional. If username and password are not provided,
    requests will be made without authentication.
    """

    def __init__(self) -> None:
        load_dotenv()
        logger.debug("Loading Alertmanager MCP configuration from environment")

        self.alertmanager_url = os.getenv("ALERTMANAGER_URL")
        self.alertmanager_username = os.getenv("ALERTMANAGER_USERNAME")
        self.alertmanager_password = os.getenv("ALERTMANAGER_PASSWORD")

        # Safe parsing with validation
        timeout_str = os.getenv("ALERTMANAGER_TIMEOUT", "30")
        try:
            self.request_timeout = int(timeout_str)
            if self.request_timeout <= 0:
                raise ValueError("Timeout must be positive")
        except ValueError as e:
            logger.error(
                "Invalid ALERTMANAGER_TIMEOUT value: %s",
                timeout_str,
                exc_info=True,
            )
            raise ValueError(
                f"Invalid ALERTMANAGER_TIMEOUT value: must be positive integer, got {timeout_str!r}"
            ) from e

        self.created_by = os.getenv("ALERTMANAGER_CREATED_BY", "alertmanager-mcp")

        if not self.alertmanager_url:
            logger.error("Missing required environment variable: ALERTMANAGER_URL")
            raise ValueError("Missing required environment variable: ALERTMANAGER_URL")

        # Log configuration (mask sensitive data)
        auth_status = "enabled" if self.alertmanager_username else "disabled"
        logger.info(
            "Alertmanager config loaded: url=%s, timeout=%ds, auth=%s, created_by=%s",
            self.alertmanager_url,
            self.request_timeout,
            auth_status,
            self.created_by,
        )


def get_config() -> Config:
    """
    Returns a new instance of the Config.

    This function loads configuration from environment variables by creating
    a new Config instance. Each call creates a fresh instance that reads
    the current environment state.

    Returns:
        Config: A configured instance with settings loaded from environment variables.

    Raises:
        ValueError: If ALERTMANAGER_URL environment variable is missing.

    Example:
        >>> config = get_config()
        >>> config.alertmanager_url
        'https://alertmanager.example.com'
    """
    return Config()
