import os
from dotenv import load_dotenv

class Config:
    """
    Configuration class for the Alertmanager MCP server.
    Loads settings from environment variables.

    Environment variables:
        ALERTMANAGER_URL (required): URL of the Alertmanager instance
        ALERTMANAGER_USERNAME (optional): Username for HTTP basic auth
        ALERTMANAGER_PASSWORD (optional): Password for HTTP basic auth
        ALERTMANAGER_TIMEOUT (optional): Request timeout in seconds (default: 30)
        ALERTMANAGER_CREATED_BY (optional): Identity for silence creation (default: alertmanager-mcp)

    Note: Authentication is optional. If username and password are not provided,
    requests will be made without authentication.
    """
    def __init__(self):
        load_dotenv()
        self.alertmanager_url = os.getenv("ALERTMANAGER_URL")
        self.alertmanager_username = os.getenv("ALERTMANAGER_USERNAME")
        self.alertmanager_password = os.getenv("ALERTMANAGER_PASSWORD")
        self.request_timeout = int(os.getenv("ALERTMANAGER_TIMEOUT", "30"))
        self.created_by = os.getenv("ALERTMANAGER_CREATED_BY", "alertmanager-mcp")

        if not self.alertmanager_url:
            raise ValueError("Missing required environment variable: ALERTMANAGER_URL")

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
        >>> print(config.alertmanager_url)
        https://alertmanager.example.com
    """
    return Config()
