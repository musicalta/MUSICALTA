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
