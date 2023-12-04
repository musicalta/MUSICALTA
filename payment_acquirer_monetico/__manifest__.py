# -*- coding: utf-8 -*-
{
    'name': "Intermédiaire de paiement Monetico",
    'summary': """Module utilisant la solution de paiement en ligne Monetico""",
    'author': "SOFTCARE Conseil",
    'website': "https://www.softcare.agency",
    'category': 'Accounting/Payment Acquirers',
    'license': 'AGPL-3',
    'version': '16.0.21.12.01',
    'installable': True,
    'depends': ['payment'],
    'data': [
        'views/templates.xml',
        'views/payment_views.xml',
        'views/payment_monetico_templates.xml',
        'views/inherited_payment_link_wizard.xml',
        'data/payment_acquirer_data.xml',
    ],
}
