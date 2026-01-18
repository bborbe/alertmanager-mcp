import logging
import re
from datetime import UTC, datetime, timedelta
from typing import Any, cast

from .client import AlertmanagerClient

logger = logging.getLogger(__name__)

# Maximum length for alert summary text
ALERT_SUMMARY_MAX_LENGTH = 200


def _extract_alert_summary(alert: dict[str, Any]) -> dict[str, Any]:
    """Extract essential fields from an alert for summary view.

    Args:
        alert: Full alert object from Alertmanager

    Returns:
        Dictionary with essential alert fields only
    """
    labels = alert.get("labels", {})
    status = alert.get("status", {})
    annotations = alert.get("annotations", {})

    return {
        "fingerprint": alert.get("fingerprint"),
        "alertname": labels.get("alertname"),
        "severity": labels.get("severity"),
        "namespace": labels.get("namespace"),
        "pod": labels.get("pod"),
        "state": status.get("state"),
        "startsAt": alert.get("startsAt"),
        "summary": annotations.get("summary", annotations.get("description", ""))[
            :ALERT_SUMMARY_MAX_LENGTH
        ],
    }


async def get_alerts(
    client: AlertmanagerClient, active_only: bool = True, filter: str | None = None
) -> dict[str, Any]:
    """
    MCP tool to get alerts from Alertmanager (summary view).

    Args:
        client: AlertmanagerClient instance
        active_only: If True, return only active alerts (default: True)
        filter: Optional filter query string (e.g., 'severity="critical"')

    Returns:
        Dictionary with 'alerts' list and 'count' of alerts

    Example:
        >>> result = await get_alerts(client, active_only=True, filter='severity="warning"')
        >>> result['count']
        5
        >>> result['alerts'][0]['alertname']
        'HighMemoryUsage'
    """
    logger.info("Getting alerts: active_only=%s, filter=%s", active_only, filter)
    alerts = client.get_alerts(active_only=active_only, filter_query=filter)
    summaries = [_extract_alert_summary(alert) for alert in alerts]
    logger.info("Retrieved %d alerts", len(summaries))
    return {"alerts": summaries, "count": len(summaries)}


async def get_alert_details(client: AlertmanagerClient, fingerprint: str) -> dict[str, Any]:
    """
    MCP tool to get complete details for a specific alert.

    Args:
        client: AlertmanagerClient instance
        fingerprint: Unique fingerprint identifier for the alert

    Returns:
        Dictionary with 'alert' containing complete alert details

    Raises:
        ValueError: If alert with given fingerprint is not found

    Example:
        >>> result = await get_alert_details(client, fingerprint="abc123def456")
        >>> result['alert']['annotations']['runbook_url']
        'https://example.com/runbook/high-memory'
    """
    logger.info("Getting alert details for fingerprint: %s", fingerprint)
    alerts = client.get_alerts(active_only=False)
    alert = next((a for a in alerts if a.get("fingerprint") == fingerprint), None)

    if not alert:
        logger.warning("Alert not found: %s", fingerprint)
        available = cast(list[str], [a.get("fingerprint") for a in alerts if a.get("fingerprint")])
        available_count = len(available)
        available_preview = ", ".join(available[:3])
        if available_count > 3:
            available_preview += f" (and {available_count - 3} more)"
        raise ValueError(
            f"Alert with fingerprint '{fingerprint}' not found. "
            f"Available fingerprints: {available_preview}"
            if available
            else f"Alert with fingerprint '{fingerprint}' not found. No alerts available."
        )

    logger.debug("Found alert: %s", alert.get("labels", {}).get("alertname"))
    return {"alert": alert}


def _parse_duration(duration_str: str) -> timedelta:
    """
    Parses a duration string (e.g., "2h", "1d") into a timedelta object.
    """
    match = re.match(r"(\d+)([hdwmy])", duration_str)
    if not match:
        raise ValueError(f"Invalid duration format: {duration_str}")
    value, unit = match.groups()
    value = int(value)
    if unit == "h":
        return timedelta(hours=value)
    if unit == "d":
        return timedelta(days=value)
    if unit == "w":
        return timedelta(weeks=value)
    if unit == "m":
        # Approximate months as 30 days
        return timedelta(days=value * 30)
    if unit == "y":
        # Approximate years as 365 days
        return timedelta(days=value * 365)
    raise ValueError(f"Unknown duration unit: {unit}")


async def silence_alert(
    client: AlertmanagerClient, fingerprint: str, duration: str, comment: str
) -> dict[str, Any]:
    """
    MCP tool to silence an alert.

    Args:
        client: AlertmanagerClient instance
        fingerprint: Unique fingerprint identifier for the alert
        duration: Duration string (e.g., "2h", "1d", "1w")
        comment: Comment explaining reason for the silence

    Returns:
        Dictionary with 'silence_id' of the created silence

    Raises:
        ValueError: If alert with given fingerprint is not found
        ValueError: If duration format is invalid

    Example:
        >>> result = await silence_alert(
        ...     client,
        ...     fingerprint="abc123",
        ...     duration="2h",
        ...     comment="Planned maintenance"
        ... )
        >>> result['silence_id']
        'silence-xyz789'
    """
    logger.info(
        "Silencing alert: fingerprint=%s, duration=%s, comment=%s",
        fingerprint,
        duration,
        comment,
    )

    # Fetch the alert to get its labels
    alerts = client.get_alerts(active_only=False)
    alert_to_silence = next(
        (alert for alert in alerts if alert.get("fingerprint") == fingerprint), None
    )

    if not alert_to_silence:
        logger.warning("Alert not found for silencing: %s", fingerprint)
        available = cast(list[str], [a.get("fingerprint") for a in alerts if a.get("fingerprint")])
        available_count = len(available)
        available_preview = ", ".join(available[:3])
        if available_count > 3:
            available_preview += f" (and {available_count - 3} more)"
        raise ValueError(
            f"Alert with fingerprint '{fingerprint}' not found. "
            f"Available fingerprints: {available_preview}"
            if available
            else f"Alert with fingerprint '{fingerprint}' not found. No alerts available."
        )

    matchers = [
        {"name": name, "value": value, "isRegex": False}
        for name, value in alert_to_silence["labels"].items()
    ]

    now = datetime.now(UTC)
    ends_at = now + _parse_duration(duration)

    logger.debug("Creating silence: matchers=%d, ends_at=%s", len(matchers), ends_at)
    result = client.create_silence(
        matchers=matchers,
        starts_at=now.isoformat(),
        ends_at=ends_at.isoformat(),
        comment=comment,
        created_by=client.config.created_by,
    )
    silence_id = result.get("silenceID")
    logger.info("Silence created: %s", silence_id)
    return {"silence_id": silence_id}


async def list_silences(client: AlertmanagerClient) -> dict[str, Any]:
    """
    MCP tool to list silences.

    Args:
        client: AlertmanagerClient instance

    Returns:
        Dictionary with 'silences' list containing all silences

    Example:
        >>> result = await list_silences(client)
        >>> len(result['silences'])
        3
        >>> result['silences'][0]['comment']
        'Maintenance window'
    """
    logger.info("Listing silences")
    silences = client.get_silences()
    logger.info("Retrieved %d silences", len(silences))
    return {"silences": silences}
