# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    student_count_max = fields.Integer(
        string='Student Count max',
        default=16,
        help='The maximum number that this teacher can supervise in one session',
    )
    additional_cost = fields.Float(
        string='Additional cost',
        help='The extra cost for this teacher',
    )
    second_mail = fields.Char(
        string='Second mail',
        help='The second mail for this teacher',
    )
    not_call_back = fields.Boolean(
        string='Do not call back',
        help='If this teacher does not want to be called back',
    )
    conservatory = fields.Char(
        string='Conservatory',
        help='The conservatory where this teacher studied or worked',
    )
    guso_number = fields.Char(
        string='GUSO number',
        help='The GUSO number of this teacher',
    )
