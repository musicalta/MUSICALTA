# -*- coding: utf-8 -*-
{
    'name': 'Monetico Payment Acquirer',
    'category': 'Accounting/Payment Acquirers',
    'summary': 'Payment Acquirer: Monetico Implementation',
    'version': '16.0',
    'author': 'DevTalents',
    'website': 'www.dev-talents.com',
    'description': """Monetico Payment Acquirer""",
    'depends': ['payment'],
    'data': [
        'views/payment_provider_views.xml',
        'views/payment_monetico_templates.xml',
        'data/payment_provider_data.xml',
    ],

    'images': ['static/description/main_screenshot.png'],
    'installable': True,
    'price': '180',
    'currency': 'EUR',
    'support': 'support@dev-talents.com',
    'license': 'OPL-1',
    'uninstall_hook': 'uninstall_hook',
}
