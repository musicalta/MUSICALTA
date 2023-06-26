from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
        required=True,
        help='Choose the teacher related to this ticket'
    )
    teacher_ids = fields.Many2many(
        related='event_id.teacher_ids'
    )
