# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class CoursesSession(models.Model):
    _name = 'courses.training'

    professor_id = fields.Many2one(
        string='Professor',
        comodel_name='hr.employee',
        required=True,
    )
    student_id= fields.Many2one(
        string='Student',
        comodel_name='res.partner',
        required=True,
    )
    event_id = fields.Many2one(
        string='Event',
        comodel_name='event.event',
        required=True,
    )
    is_supplement = fields.Boolean(
        string='Is supplement',
        default=False,
    )
    discipline_id = fields.Many2one(
        string='Discipline',
        comodel_name='employee.discipline',
        required=True,
    )
    sale_order_id = fields.Many2one(
        string='Sale Order',
        comodel_name='sale.order',
    )