# -*- coding: utf-8 -*-
{
    'name': "musicalta_employee",

    'summary': """
        Updates the hr.employee model to be considered a music class teacher""",

    'author': "Maxence Royer, IROKOO",
    'website': "https://www.irokoo.com",
    'category': 'Human Resources/Employees',
    'version': '16.0.1.0.1',
    'depends': [
        'base',
        'hr',
    ],
    'data': [
        'views/hr_employee_view.xml',
    ],
}
