# -*- coding: utf-8 -*-
{
    'name': "musicalta_event",

    'summary': """
        This module links many employee as teachers to one event and manage
        this event in terms of teacher informations (additonnal cost or max student number)""",

    'author': "Maxence Royer , IROKOO",
    'website': "https://www.irokoo.com",
    'category': 'Marketing/Events',
    'version': '16.0.1.0.0',
    'depends': [
        'base',
        'hr',
        'event',
        'event_sale',
    ],
    'data': [
        'views/event_event_views.xml',
        'views/event_registration_view.xml',
        'views/event_ticket_view.xml',
        'views/sale_order_view.xml',
    ],

}
