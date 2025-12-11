from typing import Dict, Any, Optional
from urllib.parse import urljoin
import requests
from requests.auth import HTTPBasicAuth

from .config import Config

class AlertmanagerClient:
    """
    HTTP client for interacting with the Alertmanager API.
    """
    def __init__(self, config: Config):
        self.config = config
        self.session = requests.Session()
        if config.alertmanager_username and config.alertmanager_password:
            self.session.auth = HTTPBasicAuth(
                config.alertmanager_username,
                config.alertmanager_password
            )

    def _request(self, method: str, path: str, **kwargs) -> Dict[str, Any]:
        """
        Internal method to make HTTP requests to the Alertmanager API.
        """
        # Ensure base URL ends with / for urljoin to work correctly
        base_url = self.config.alertmanager_url
        if not base_url.endswith('/'):
            base_url += '/'
        url = urljoin(base_url, path.lstrip('/'))
        try:
            response = self.session.request(method, url, timeout=self.config.request_timeout, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise requests.exceptions.HTTPError(
                f"HTTP error for {method} {path}: {e}",
                response=e.response
            ) from e

    def get_alerts(self, active_only: bool = True, filter_query: Optional[str] = None) -> list:
        """
        Fetch alerts from Alertmanager.
        """
        params = {"active": str(active_only).lower()}
        if filter_query:
            params["filter"] = filter_query
        return self._request("GET", "/api/v2/alerts", params=params)

    def get_silences(self) -> list:
        """
        Fetch silences from Alertmanager.
        """
        return self._request("GET", "/api/v2/silences")

    def create_silence(self, matchers: list, starts_at: str, ends_at: str, comment: str, created_by: str) -> dict:
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
        return self._request("POST", "/api/v2/silences", json=payload)

