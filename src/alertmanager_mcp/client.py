import logging
from typing import Any, cast
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth

from .config import Config

logger = logging.getLogger(__name__)


class AlertmanagerClient:
    """
    HTTP client for interacting with the Alertmanager API.
    """

    def __init__(self, config: Config) -> None:
        self.config = config
        self.session = requests.Session()
        if config.alertmanager_username and config.alertmanager_password:
            self.session.auth = HTTPBasicAuth(
                config.alertmanager_username, config.alertmanager_password
            )
            logger.debug("HTTP Basic Auth configured for Alertmanager client")
        else:
            logger.debug("No authentication configured for Alertmanager client")

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        """
        Internal method to make HTTP requests to the Alertmanager API.

        Returns:
            Response data (can be dict, list, or other JSON types).
        """
        # Ensure base URL ends with / for urljoin to work correctly
        base_url = self.config.alertmanager_url
        if base_url is None:
            raise ValueError("Alertmanager URL is not configured")
        if not base_url.endswith("/"):
            base_url += "/"
        url = urljoin(base_url, path.lstrip("/"))

        logger.debug("Alertmanager API request: %s %s", method, path)
        if kwargs.get("params"):
            logger.debug("Request params: %s", kwargs["params"])

        try:
            response = self.session.request(
                method, url, timeout=self.config.request_timeout, **kwargs
            )
            response.raise_for_status()
            logger.debug(
                "Alertmanager API response: %s %s -> %d",
                method,
                path,
                response.status_code,
            )
            return response.json()
        except requests.exceptions.HTTPError as e:
            logger.error(
                "Alertmanager API error: %s %s -> %s",
                method,
                path,
                e,
                exc_info=True,
            )
            raise requests.exceptions.HTTPError(
                f"HTTP error for {method} {path}: {e}", response=e.response
            ) from e

    def get_alerts(
        self, active_only: bool = True, filter_query: str | None = None
    ) -> list[dict[str, Any]]:
        """
        Fetch alerts from Alertmanager.

        Returns:
            List of alert dictionaries from the Alertmanager API.
        """
        params = {"active": str(active_only).lower()}
        if filter_query:
            params["filter"] = filter_query
        return cast(list[dict[str, Any]], self._request("GET", "/api/v2/alerts", params=params))

    def get_silences(self) -> list[dict[str, Any]]:
        """
        Fetch silences from Alertmanager.

        Returns:
            List of silence dictionaries from the Alertmanager API.
        """
        return cast(list[dict[str, Any]], self._request("GET", "/api/v2/silences"))

    def create_silence(
        self,
        matchers: list[dict[str, str]],
        starts_at: str,
        ends_at: str,
        comment: str,
        created_by: str,
    ) -> dict[str, Any]:
        """
        Create a silence in Alertmanager.
        """
        payload = {
            "matchers": matchers,
            "startsAt": starts_at,
            "endsAt": ends_at,
            "comment": comment,
            "createdBy": created_by,
        }
        return cast(dict[str, Any], self._request("POST", "/api/v2/silences", json=payload))
