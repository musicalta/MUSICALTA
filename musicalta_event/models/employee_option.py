# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class EmployeeOption(models.Model):
    _name = 'employee.option'
    _description = 'This model represents an option like a musical level'

    name = fields.Char(
        string='Option',
        required=True,
    )