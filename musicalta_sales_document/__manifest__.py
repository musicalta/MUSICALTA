# -*- coding: utf-8 -*-

{
    "name": "Sales Inscriptions Documents management for Musicalta",
    "version": "16.0.1.0.0",
    "summary": """Add documents management in sales inscriptions for Musicalta.""",
    "category": "customization",
    "website": "https://irokoo.fr",
    "author": "IROKOO, Olimalt Chahidov",
    "license": "LGPL-3",
    "depends": [
        "base",
        "musicalta_sales",
        "documents",
    ],
    "data": [
        # VIEWS
        "views/sale_inscription_views.xml",
        "views/documents_folder_views.xml",
    ],
    "installable": True,
}
