import logging
import random
import time
import requests

_logger = logging.getLogger(__name__)

_RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class HttpClient:
    def __init__(self, *, rps=3, max_retries=5, backoff_base=0.5, backoff_cap=8.0, timeout=15):
        self._min_interval = 1.0 / float(rps) if rps else 0.0
        self._max_retries = int(max_retries)
        self._backoff_base = float(backoff_base)
        self._backoff_cap = float(backoff_cap)
        self._timeout = int(timeout)
        self._last_call = 0.0

    def request(self, method, url, *, headers=None, params=None):
        for attempt in range(self._max_retries + 1):
            self._throttle()
            try:
                resp = requests.request(method, url, headers=headers, params=params, timeout=self._timeout)
            except requests.RequestException as exc:
                if attempt >= self._max_retries:
                    raise
                self._sleep(attempt, reason=str(exc))
                continue

            if resp.status_code in _RETRYABLE_STATUS:
                if attempt >= self._max_retries:
                    resp.raise_for_status()
                self._sleep(attempt, retry_after=resp.headers.get('Retry-After'), reason='HTTP %s' % resp.status_code)
                continue

            resp.raise_for_status()
            return resp

    def _throttle(self):
        if not self._min_interval:
            return
        now = time.monotonic()
        wait = (self._last_call + self._min_interval) - now
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def _sleep(self, attempt, *, retry_after=None, reason=''):
        if retry_after:
            try:
                time.sleep(float(retry_after))
                _logger.info('Reintentando por Retry-After. intento=%s motivo=%s', attempt + 1, reason)
                return
            except ValueError:
                pass

        base = min(self._backoff_cap, self._backoff_base * (2 ** attempt))
        time.sleep(base + random.uniform(0, base * 0.25))
        _logger.info('Reintentando después del backoff. intento=%s motivo=%s', attempt + 1, reason)
