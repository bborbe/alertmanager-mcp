from unittest.mock import Mock

import pytest
from requests import HTTPError

from alertmanager_mcp.client import AlertmanagerClient
from alertmanager_mcp.config import Config


def test_get_alerts_success(mocker):
    """
    Test successful fetching of alerts.
    """
    mock_response = Mock()
    mock_response.json.return_value = [{"labels": {"alertname": "TestAlert"}}]
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.Session.request", return_value=mock_response)

    def mock_getenv(key, default=None):
        env_vars = {"ALERTMANAGER_URL": "http://fake-alertmanager", "ALERTMANAGER_TIMEOUT": "30"}
        return env_vars.get(key, default)

    mocker.patch("os.getenv", side_effect=mock_getenv)
    config = Config()
    client = AlertmanagerClient(config)
    alerts = client.get_alerts()

    assert len(alerts) == 1
    assert alerts[0]["labels"]["alertname"] == "TestAlert"


def test_create_silence_success(mocker):
    """
    Test successful creation of a silence.
    """
    mock_response = Mock()
    mock_response.json.return_value = {"silenceID": "test-silence-id"}
    mock_response.raise_for_status.return_value = None
    mocker.patch("requests.Session.request", return_value=mock_response)

    def mock_getenv(key, default=None):
        env_vars = {"ALERTMANAGER_URL": "http://fake-alertmanager", "ALERTMANAGER_TIMEOUT": "30"}
        return env_vars.get(key, default)

    mocker.patch("os.getenv", side_effect=mock_getenv)

    config = Config()
    client = AlertmanagerClient(config)
    result = client.create_silence([], "start", "end", "comment", "creator")

    assert result["silenceID"] == "test-silence-id"


def test_http_error(mocker):
    """
    Test that HTTP errors are raised.
    """
    mock_response = Mock()
    mock_response.raise_for_status.side_effect = HTTPError
    mocker.patch("requests.Session.request", return_value=mock_response)

    def mock_getenv(key, default=None):
        env_vars = {"ALERTMANAGER_URL": "http://fake-alertmanager", "ALERTMANAGER_TIMEOUT": "30"}
        return env_vars.get(key, default)

    mocker.patch("os.getenv", side_effect=mock_getenv)

    config = Config()
    client = AlertmanagerClient(config)
    with pytest.raises(HTTPError):
        client.get_alerts()
