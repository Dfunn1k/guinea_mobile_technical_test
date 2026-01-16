import json
import logging
from datetime import datetime
from typing import Any

from odoo import models
from odoo.exceptions import UserError

from ..services.http_client import HttpClient
from ..services.partner_sync import log_event

_logger = logging.getLogger(__name__)


class ExternalSyncService(models.AbstractModel):
    _name = 'external.sync.service'
    _description = 'Servicio de sincronización con sistema externo'

    def _config(self) -> dict[str, Any]:
        icp = self.env['ir.config_parameter'].sudo()
        return {
            "base_url": icp.get_param('external.api.base_url', 'http://fastapi:8000'),
            "token": icp.get_param('external.api.token'),
            "rps": float(icp.get_param('external.api.rps', '3')),
            "max_retries": int(icp.get_param('external.api.max_retries', '5')),
        }

    def sync_partner(self, payload: dict[str, Any]) -> dict[str, Any]:
        cfg = self._config()
        if not cfg.get('token'):
            raise UserError('No hay un token configurado para la integración externa.')

        url = f"{cfg['base_url'].rstrip('/')}/rpc"
        headers = {
            'Authorization': f"Bearer {cfg['token']}",
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        body = {
            'jsonrpc': '2.0',
            'method': 'partner.sync',
            'params': payload,
            'id': datetime.utcnow().timestamp(),
        }
        client = HttpClient(rps=cfg['rps'], max_retries=cfg['max_retries'])
        log_event(
            _logger,
            'external_sync_request',
            url=url,
            payload=payload,
        )
        resp = client.request('POST', url, headers=headers, json=body)
        data = resp.json() if resp.content else {}
        if 'error' in data:
            log_event(
                _logger,
                'external_sync_error',
                error=data.get('error'),
                payload=payload,
            )
            raise UserError('Error en sincronización externa: %s' % json.dumps(data.get('error')))
        return data.get('result')
