# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    discipline_ids = fields.Many2many(
        string='Disciplines',
        comodel_name='employee.discipline',
        required=True,
    )
    options_ids = fields.Many2many(
        string='Options',
        comodel_name='employee.option',
    )
    
