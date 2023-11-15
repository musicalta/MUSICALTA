# -*- coding: utf-8 -*-

{
    "name": "Sales For musicalta",
    "version": "16.0.1.0.0",
    "summary": """Add Sales customization.""",
    "category": "customization",
    "website": "https://irokoo.fr",
    "author": "IROKOO, Charles-Edouard Toutain",
    "license": "LGPL-3",
    "depends": [
        "base",
        "product",
        "sale_management",
        "musicalta_event",
    ],
    "data": [
        # #DATA
        # "data/ir_sequence_data.xml",
        # # SECURITY
        "security/ir_model_access.xml",
        # WIZARDS
        "wizards/wizard_event_inscription.xml",
        # # VIEWS
        "views/sale_order_views.xml",
        "views/lunch_order_views.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}