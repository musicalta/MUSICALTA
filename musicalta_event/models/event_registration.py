from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
        required=True,
        help='Choose the teacher related to this ticket',
        related='event_ticket_id.teacher_id'
    )
    teacher_ids = fields.Many2many(
        related='event_id.teacher_ids'
    )
    discipline_id = fields.Many2one(
        'employee.discipline',
        string='Discipline',
    )
    option_id = fields.Many2one(
        'employee.option',
        string='Option',
    )
    number_of_repas = fields.Integer(
        string='Nombre de repas',
        default=0,
    )
