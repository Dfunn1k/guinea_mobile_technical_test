from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    decolecta_api_token = fields.Char(
        string='Decolecta API Token',
        config_parameter='decolecta.api.token',
        help='Token para consultas RUC, DNI y tipo de cambio. Puedes conseguirlo en Decolecta.',
    )
    external_api_base_url = fields.Char(
        string='External API Base URL',
        config_parameter='external.api.base_url',
        help='Base URL del sistema externo (FastAPI).',
    )
    external_api_token = fields.Char(
        string='External API Token',
        config_parameter='external.api.token',
        help='Token para autenticación con el sistema externo.',
    )
    external_api_rps = fields.Float(
        string='External API RPS',
        config_parameter='external.api.rps',
        default=3.0,
        help='Límite de requests por segundo hacia el sistema externo.',
    )
    external_api_max_retries = fields.Integer(
        string='External API Max Retries',
        config_parameter='external.api.max_retries',
        default=5,
        help='Número máximo de reintentos con backoff.',
    )
