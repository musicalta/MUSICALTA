# -*- coding: utf-8 -*-

{
    "name": "Contact Specifics for Musicalta",
    "version": "16.0.3.0.0",
    "summary": """Add product specifics for Musicalta.""",
    "category": "customization",
    "website": "https://irokoo.fr",
    "author": "IROKOO, Charles-Edouard Toutain",
    "license": "LGPL-3",
    "depends": [
        "base",
        "contacts",
        "hr",
    ],
    "data": [
        # DATA
        "data/ir_sequence_data.xml",
        # VIEWS
        "views/res_partner_views.xml",
    ],
    "installable": True,
}
