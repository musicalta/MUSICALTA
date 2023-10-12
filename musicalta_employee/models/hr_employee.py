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
    contact_info = fields.Char(
        string='Contact Info',
        help='The contact info for this teacher',
    )
    website = fields.Char(
        string='Website',
        help='The website for this teacher',
    )
    private_email = fields.Char(
        readonly=False,
    )
