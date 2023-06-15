# -*- coding: utf-8 -*-

{
    "name": "Event Specifics for Musicalta",
    "version": "16.0.1.0.0",
    "summary": """Add Event specifics for Musicalta.""",
    "category": "customization",
    "website": "https://irokoo.fr",
    "author": "IROKOO, Charles-Edouard Toutain",
    "license": "LGPL-3",
    "depends": [
        "base",
        "event",
    ],
    "data": [
        # SECURITY
        "security/ir.model.access.csv",
        # VIEWS
        "views/event_parent.xml",
    ],
    "installable": True,
    "license": "LGPL-3",
}