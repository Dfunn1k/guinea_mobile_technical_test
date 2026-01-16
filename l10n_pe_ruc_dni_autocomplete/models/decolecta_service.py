# -*- coding: utf-8 -*-
import logging
from odoo import models
from odoo.exceptions import UserError
from ..schemas.sunat_schema import SunatDTO
from ..schemas.reniec_schema import ReniecDTO
from ..services.http_client import HttpClient

_logger = logging.getLogger(__name__)


class DecolectaServiceMixin(models.AbstractModel):
    _name = 'decolecta.service'
    _description = 'Servicio de integración con Decolecta'

    _BASE_URL = 'https://api.decolecta.com/v1'

    def _config(self):
        icp = self.env['ir.config_parameter'].sudo()
        return {
            'token': icp.get_param('decolecta.api.token'),
            'base_url': self._BASE_URL,
        }

    def fetch_ruc_payload(self, ruc: str) -> dict:
        cfg = self._config()
        if not cfg['token']:
            raise UserError("No hay un token configurado para la integración con Decolecta.")
        url = '%s/sunat/ruc/full' % cfg['base_url']
        headers = {
            'Authorization': 'Bearer %s' % cfg['token'],
            'Accept': 'application/json',
        }
        _logger.info('Consultando Decolecta RUC=%s', ruc)
        client = HttpClient(rps=3, max_retries=5)
        resp = client.request('GET', url, headers=headers, params={'numero': ruc})
        payload = resp.json() or {}
        return payload

    def fetch_ruc(self, ruc: str) -> tuple[dict, SunatDTO]:
        payload = self.fetch_ruc_payload(ruc)
        return payload, SunatDTO.from_payload(payload)

    def fetch_dni_payload(self, dni: str) -> dict:
        cfg = self._config()
        if not cfg['token']:
            raise UserError("No hay un token configurado para la integración con Decolecta.")
        url = '%s/reniec/dni' % cfg['base_url']
        headers = {
            'Authorization': 'Bearer %s' % cfg['token'],
            'Accept': 'application/json',
        }
        _logger.info('Consultando Decolecta DNI=%s', dni)
        client = HttpClient(rps=3, max_retries=5)
        resp = client.request('GET', url, headers=headers, params={'numero': dni})
        payload = resp.json() or {}
        return payload

    def fetch_dni(self, dni: str) -> tuple[dict, ReniecDTO]:
        payload = self.fetch_dni_payload(dni)
        return payload, ReniecDTO.from_payload(payload)
