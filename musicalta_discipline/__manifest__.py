# -*- coding: utf-8 -*-
{
    'name': "musicalta_discipline",

    'summary': """
        This module add a new data design model "employee.discipline"
    """,
    "author": "IROKOO, Maxence Royer",
    "website": "https://irokoo.fr",
    'category': 'customization',
    'version': '16.0.1.0.1',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/employee_disciplines_views.xml',
        'views/hr_employee_view.xml',
    ],
    'license': 'LGPL-3',
    'installable': True,
}
