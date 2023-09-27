# -*- coding: utf-8 -*-
{
    'name': "musicalta_product",

    'summary': """Specific product for Musicalta""",
    'author': "IROKOO",
    'website': "https://www.irokoo.com",
    'category': 'Customizations',
    'version': '0.1',
    'depends': [
        'base',
        'sale',
    ],
    'data': [
        # DATA
        'data/event_ticket.xml',
        # VIEWS
        'views/product_product_views.xml',
    ],
}
