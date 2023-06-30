# -*- coding: utf-8 -*-

{
    "name": "Event Specifics for Musicalta",
    "version": "16.0.1.0.0",
    "summary": """Add Event specifics for Musicalta.""",
    "category": "customization",
    "website": "https://irokoo.fr",
    "author": "IROKOO,  Charles-Edouard Toutain, Maxence Royer",
    "license": "LGPL-3",
    "depends": [
        "base",
        "hr",
        "event",
        "event_sale",
    ],
    "data": [
        # SECURITY
        "security/ir.model.access.csv",
        # VIEWS
        "views/event_event_views.xml",
        "views/event_parent.xml",
        "views/event_registration_view.xml",
        "views/event_ticket_view.xml",
        "views/sale_order_view.xml",
    ],
    "installable": True,
}
