# -*- coding: utf-8 -*-

{
    "name": "Event Specifics for Musicalta",
    "version": "16.1.3.0.0",
    "summary": """Add Event specifics for Musicalta.""",
    "category": "customization",
    "website": "https://irokoo.fr",
    "author": "IROKOO,  Charles-Edouard Toutain, Maxence Royer",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
        "musicalta_discipline",
        "event",
        "event_sale",
    ],
    "data": [
        # DATA
        "data/ir_cron_data.xml",
        "data/mail_template_data.xml",
        # SECURITY
        "security/ir_model_access.xml",
        # VIEWS
        "views/event_event_views.xml",
        "views/event_event.xml",
        "views/event_registration_view.xml",
        "views/event_ticket_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
