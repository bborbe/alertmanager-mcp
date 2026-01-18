from datetime import timedelta
from unittest.mock import Mock

import pytest

from alertmanager_mcp.mcp_tools import (
    _parse_duration,
    get_alert_details,
    get_alerts,
    silence_alert,
)


@pytest.mark.parametrize(
    "duration_str, expected",
    [
        ("1h", timedelta(hours=1)),
        ("2d", timedelta(days=2)),
        ("3w", timedelta(weeks=3)),
    ],
)
def test_parse_duration_success(duration_str, expected):
    """
    Test successful parsing of duration strings.
    """
    assert _parse_duration(duration_str) == expected


def test_parse_duration_invalid():
    """
    Test that invalid duration strings raise ValueError.
    """
    with pytest.raises(ValueError):
        _parse_duration("1x")


@pytest.mark.asyncio
async def test_get_alerts_tool(mocker):
    """
    Test the get_alerts tool returns summary format.
    """
    mock_client = Mock()
    mock_client.get_alerts.return_value = [
        {
            "fingerprint": "abc123",
            "labels": {
                "alertname": "TestAlert",
                "severity": "critical",
                "namespace": "default",
                "pod": "test-pod",
            },
            "status": {"state": "active"},
            "startsAt": "2025-12-11T10:00:00Z",
            "annotations": {"summary": "Test alert summary"},
        }
    ]
    result = await get_alerts(mock_client, active_only=True)

    assert result["count"] == 1
    assert result["alerts"][0]["fingerprint"] == "abc123"
    assert result["alerts"][0]["alertname"] == "TestAlert"
    assert result["alerts"][0]["severity"] == "critical"
    assert result["alerts"][0]["namespace"] == "default"
    assert result["alerts"][0]["pod"] == "test-pod"
    assert result["alerts"][0]["state"] == "active"
    assert result["alerts"][0]["summary"] == "Test alert summary"


@pytest.mark.asyncio
async def test_get_alert_details(mocker):
    """
    Test the get_alert_details tool returns complete alert.
    """
    mock_client = Mock()
    full_alert = {
        "fingerprint": "abc123",
        "labels": {
            "alertname": "TestAlert",
            "severity": "critical",
            "namespace": "default",
            "pod": "test-pod",
        },
        "status": {"state": "active"},
        "startsAt": "2025-12-11T10:00:00Z",
        "annotations": {
            "summary": "Test alert summary",
            "description": "Full description",
            "runbook_url": "https://example.com/runbook",
        },
    }
    mock_client.get_alerts.return_value = [full_alert]
    result = await get_alert_details(mock_client, fingerprint="abc123")

    assert result["alert"] == full_alert
    assert result["alert"]["annotations"]["runbook_url"] == "https://example.com/runbook"


@pytest.mark.asyncio
async def test_get_alert_details_not_found(mocker):
    """
    Test get_alert_details when alert is not found.
    """
    mock_client = Mock()
    mock_client.get_alerts.return_value = []
    with pytest.raises(ValueError, match="not found"):
        await get_alert_details(mock_client, "nonexistent")


@pytest.mark.asyncio
async def test_silence_alert_tool_not_found():
    """
    Test silence_alert when alert is not found.
    """
    mock_client = Mock()
    mock_client.get_alerts.return_value = []
    with pytest.raises(ValueError, match="not found"):
        await silence_alert(mock_client, "123", "1h", "comment")
