# -*- coding: utf-8 -*-
import logging
from odoo import models
from odoo.exceptions import UserError
from ..schemas.sunat_schema import SunatDTO
from ..schemas.reniec_schema import ReniecDTO
from ..services.decolecta_client import fetch_decolecta_payload

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
        payload = fetch_decolecta_payload(
            base_url=cfg['base_url'],
            token=cfg['token'],
            endpoint='sunat/ruc/full',
            params={'numero': ruc},
        )
        return payload

    def fetch_ruc(self, ruc: str) -> tuple[dict, SunatDTO]:
        payload = self.fetch_ruc_payload(ruc)
        if not payload or not payload.get('numero_documento'):
            raise UserError("No se encontró información para el RUC solicitado.")
        return payload, SunatDTO.from_payload(payload)

    def fetch_dni_payload(self, dni: str) -> dict:
        cfg = self._config()
        if not cfg['token']:
            raise UserError("No hay un token configurado para la integración con Decolecta.")
        payload = fetch_decolecta_payload(
            base_url=cfg['base_url'],
            token=cfg['token'],
            endpoint='reniec/dni',
            params={'numero': dni},
        )
        return payload

    def fetch_dni(self, dni: str) -> tuple[dict, ReniecDTO]:
        payload = self.fetch_dni_payload(dni)
        if not payload or not payload.get('document_number'):
            raise UserError("No se encontró información para el DNI solicitado.")
        return payload, ReniecDTO.from_payload(payload)
