from odoo import api, fields, models


class EventTicket(models.Model):
    _inherit = 'event.event.ticket'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
    )
    teacher_ids = fields.Many2many(
        related='event_id.teacher_ids'
    )
    discipline_ids = fields.Many2many(
        related='teacher_id.discipline_ids'
    )
    discipline_id = fields.Many2one(
        string='Discipline',
        comodel_name='employee.discipline',
        readonly=True
    )
