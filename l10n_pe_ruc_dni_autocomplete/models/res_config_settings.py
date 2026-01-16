from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    decolecta_api_token = fields.Char(
        string='Decolecta API Token',
        config_parameter='decolecta.api.token',
        help='Token para consultas RUC, DNI y tipo de cambio. Puedes conseguirlo en Decolecta.',
    )
