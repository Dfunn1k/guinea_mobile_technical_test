from odoo import _, api, fields, models
from ..schemas.sunat_schema import SunatDTO

_SUNAT_STATE = [
    ('HABIDO', 'HABIDO'),
    ('NO HABIDO', 'NO HABIDO')
]

class ResPartner(models.Model):
    _inherit = 'res.partner'

    sunat_state = fields.Selection(
        string='Estado',
        selection=_SUNAT_STATE,
        index='btree',
    )
    sunat_condition = fields.Char(string='Condición')
    sunat_ubigeo = fields.Char(string='Ubigeo')
    sunat_is_withholding_agent = fields.Boolean(
        string='¿Agente de retención?',
        default=False
    )
    sunat_is_good_taxprayer = fields.Boolean(
        string='¿Buen contribuyente?',
        default=False
    )
    sunat_company_type = fields.Char(string='Tipo')
    sunat_economy_activity = fields.Char(string='Actividad económica')
    sunat_workers = fields.Integer(string='Número trabajadores')
    sunat_invoicing = fields.Char(string='Tipo de facturación')
    sunat_accountant = fields.Char(string='Tipo de contabildiad')
    sunat_foreign_trade = fields.Char(string='Comercio exterior')
    is_visible_ruc = fields.Boolean(
        string='¿RUC visible?',
        default=False,
        compute='_compute_visible_documents',
        store=True
    )
    is_visible_dni = fields.Boolean(
        string='¿DNI visible?',
        default=False,
        compute='_compute_visible_documents',
        store=True
    )

    @api.depends('country_id', 'l10n_latam_identification_type_id')
    def _compute_visible_documents(self):
        for rec in self:
            country = self.env.ref('base.pe')
            dni = self.env.ref('l10n_pe.it_DNI')
            ruc = self.env.ref('l10n_pe.it_RUC')
            if not rec.country_id or rec.country_id.id != country.id:
                rec.is_visible_ruc = False
                rec.is_visible_dni = False

            if rec.l10n_latam_identification_type_id.id.id == dni.id:
                rec.is_visible_dni = True
                rec.is_visible_ruc = False
            elif rec.l10n_latam_identification_type_id.id == ruc.id:
                rec.is_visible_dni = False
                rec.is_visible_ruc = True

    def _detect_document_type(self):
        self.ensure_one()
        vat = (self.vat or '').strip()

        document_type = self.l10n_latam_identification_type_id
        if document_type:
            haystack = ('%s %s' % (document_type.name or '', document_type.description or '')).upper()
            if 'RUC' in haystack:
                return 'ruc'
            if 'DNI' in haystack:
                return 'dni'

        if vat.isdigit() and len(vat) == 11:
            return 'ruc'
        if vat.isdigit() and len(vat) == 8:
            return 'dni'
        return None

    def action_complete_from_decolecta(self):
        self.ensure_one()

        svc = self.env['decolecta.service']
        try:
            payload, dto = svc.fetch_ruc(self.vat)
            self._apply_ruc(dto=dto)
        except:
            pass

    def _apply_ruc(self, dto: SunatDTO):
        self.ensure_one()


        vals = {
            'name': dto.razon_social,
            'vat': dto.numero_documento,
            'sunat_state': dto.estado,
            'sunat_condition': dto.condicion,
            'street': dto.direccion,
            'sunat_ubigeo': dto.ubigeo,
            'sunat_is_withholding_agent': dto.es_agente_retencion,
            'sunat_is_good_taxpayer': dto.es_buen_contribuyente,
            'sunat_company_type': dto.tipo,
            'sunat_economy_activity': dto.actividad_economica,
            'sunat_workers': dto.numero_trabajadores,
            'sunat_invoicing': dto.tipo_facturacion,
            'sunat_accountant': dto.tipo_contabilidad,
            'sunat_foreign_trade': dto.comercio_exterior,
        }

        pe_country = self.env.ref('base.pe')
        state = self._find_department(dto.departamento, pe_country)
        city = self._find_city(dto.provincia, state, pe_country)
        district = self._find_district(dto.distrito, city.id)

        vals['state_id'] = state.id
        vals['city_id'] = city.id
        vals['l10n_pe_district'] = district.id
        vals['company_type'] = 'company'
        vals['type'] = 'contact'
        state = None

        self.write(vals)

    def _find_district(self, district_name, city_id):
        return self.env['l10n_pe.res.city.district'].search([
            ('city_id', '=', city_id.id),
            ('name', '=ilike', district_name)
        ], limit=1)

    def _find_city(self, city_name, state_id, country_id):
        return self.env['res.city'].search([
            ('country_id', '=', country_id.id),
            ('state_id', '=', state_id.id)
            ('name', '=ilike', city_name)
        ], limit=1)

    def _find_department(self, department_name, country_id):
        if not department_name or not country_id:
            return False
        return self.env['res.country.state'].search([
            ('country_id', '=', country_id.id),
            ('name', '=ilike', department_name)
        ], limit=1)
