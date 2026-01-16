{
    'name': 'RUC/DNI - AUTOCOMPLETE',
    'version': '19.0.1.1.0',
    'summary': 'Autocompleta partners con RUC/DNI usando Decolecta (SUNAT/RENIEC)',
    'category': 'Localization',
    'license': 'LGPL-3',
    'depends': [
        'l10n_pe',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'views/res_partner_views.xml'
    ],
    'installable': True,
    'application': False,
    'auto_install': True
}
