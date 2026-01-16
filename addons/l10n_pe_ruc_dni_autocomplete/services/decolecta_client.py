import logging
from typing import Any

from .http_client import HttpClient

_logger = logging.getLogger(__name__)


def fetch_decolecta_payload(
    *,
    base_url: str,
    token: str,
    endpoint: str,
    params: dict[str, Any],
    rps: float = 3,
    max_retries: int = 5,
) -> dict[str, Any]:
    url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        'Authorization': f"Bearer {token}",
        'Accept': 'application/json',
    }
    _logger.info('Consultando Decolecta endpoint=%s params=%s', endpoint, params)
    client = HttpClient(rps=rps, max_retries=max_retries)
    resp = client.request('GET', url, headers=headers, params=params)
    return resp.json() or {}
