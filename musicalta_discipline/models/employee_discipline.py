# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class EmployeeDiscipline(models.Model):
    _name = 'employee.discipline'
    _description = 'This model represents a discipline like a piano or guitar'

    name = fields.Char(
        string='Discipline',
        required=True,
    )
    teacher_ids = fields.Many2many(
        string='Teachers',
        comodel_name='hr.employee',
        help=_('Teachers who master this discipline')
    )
    is_harpe = fields.Boolean(
        string='Is harpe',
        default=False,
    )
    is_piano = fields.Boolean(
        string='Is piano',
        default=False,
    )
    product_work_room_ids = fields.Many2many(
        'product.template', string='Work rooms'
    )
