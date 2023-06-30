# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'

    discipline_ids = fields.Many2many(
        string='Disciplines',
        comodel_name='employee.discipline',
        compute='_compute_discipline_ids'
    )

    def _compute_discipline_ids(self):
        disciplines = self.env['employee.discipline'].search([])
        for record in self:
            record.discipline_ids = False
            for discipline in disciplines:
                if record.id in discipline.teacher_ids.ids:
                    record.discipline_ids |= discipline
