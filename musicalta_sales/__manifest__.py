# -*- coding: utf-8 -*-

{
    "name": "Sales For musicalta",
    "version": "16.0.7.1.1",
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
        "musicalta_contact",
        "product_pack",
        "sale_product_pack",
        "mail_activity_team",
        "sale_advance_payment",

    ],
    "data": [
        # #DATA
        "data/mail_data.xml",
        # "data/ir_sequence_data.xml",
        # # SECURITY
        "security/ir_model_access.xml",
        # REPORTS
        "reports/sale_report.xml",
        "reports/sale_inscription_badge_report.xml",
        "reports/session_prof_badge_report.xml",
        # # VIEWS
        "views/external_layout_template.xml",
        "views/sale_report_saleorder_document_template.xml",
        "views/sale_inscription.xml",
        "views/sale_order_views.xml",
        "views/lunch_order_views.xml",
        "views/musicalta_sales_menu.xml",
        "views/sale_inscription_location_views.xml",
        "views/sale_inscription_origin_views.xml",
        "views/event_type.xml",
        "views/res_partner.xml",
        "views/product_pricelist_item_views.xml",
        "views/mail_activity_team_views.xml",
        # WIZARDS
        "wizard/sale_advance_payment_wzd.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}
