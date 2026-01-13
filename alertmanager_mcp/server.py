from typing import Any

from fastmcp import FastMCP

from . import mcp_tools
from .client import AlertmanagerClient
from .config import get_config

# Initialize MCP server
mcp = FastMCP("Alertmanager MCP")

# Initialize config and client
config = get_config()
client = AlertmanagerClient(config)


@mcp.tool(description="Get alerts from Alertmanager (summary view)")
async def get_alerts(active_only: bool = True, filter: str | None = None) -> dict[str, Any]:
    """Fetch alerts from Alertmanager with essential fields only.

    Args:
        active_only: Fetch only active alerts (default: True)
        filter: Optional Alertmanager filter query string

    Returns:
        Dictionary containing list of alert summaries
    """
    return await mcp_tools.get_alerts(client, active_only=active_only, filter=filter)


@mcp.tool(description="Get detailed information for a specific alert")
async def get_alert_details(fingerprint: str) -> dict[str, Any]:
    """Fetch complete details for a specific alert by fingerprint.

    Args:
        fingerprint: The fingerprint of the alert to retrieve

    Returns:
        Dictionary containing complete alert details
    """
    return await mcp_tools.get_alert_details(client, fingerprint=fingerprint)


@mcp.tool(description="Silence an alert in Alertmanager")
async def silence_alert(fingerprint: str, duration: str, comment: str) -> dict[str, Any]:
    """Create a silence for an alert.

    Args:
        fingerprint: The fingerprint of the alert to silence
        duration: Duration of the silence (e.g., "2h", "1d", "1w")
        comment: A comment explaining the reason for the silence

    Returns:
        Dictionary containing silence_id
    """
    return await mcp_tools.silence_alert(
        client, fingerprint=fingerprint, duration=duration, comment=comment
    )


@mcp.tool(description="List silences from Alertmanager")
async def list_silences() -> dict[str, Any]:
    """List existing silences from Alertmanager.

    Returns:
        Dictionary containing list of silences
    """
    return await mcp_tools.list_silences(client)


if __name__ == "__main__":
    mcp.run()
