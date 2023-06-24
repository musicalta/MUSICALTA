from odoo import api, fields, models


class EventTickets(models.Model):
    _inherit = 'event.event.ticket'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
        required=True,
        help='Choose the teacher related to this ticket'
    )
