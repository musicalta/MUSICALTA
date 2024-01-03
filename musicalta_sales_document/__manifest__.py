# -*- coding: utf-8 -*-

{
    "name": "Sales Inscriptions Documents management for Musicalta",
    "version": "16.0.3.0.0",
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
        "security/ir_model_access.xml",
        "views/sale_inscription_views.xml",
        "views/documents_folder_views.xml",
        "views/documents_tag_views.xml",
        "wizards/download_attachments_wizard_views.xml",
    ],
    "installable": True,
}
