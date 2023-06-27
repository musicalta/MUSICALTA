from odoo import api, fields, models


class Event(models.Model):
    _inherit = 'event.event'

    teacher_ids = fields.Many2many(
        string='Teachers',
        comodel_name='hr.employee',
        relation='employee_event_rel_id',
        column1='employee_id',
        column2='event_id'
    )
    limit_registration_by_teacher = fields.Boolean(
        related='event_type_id.limit_registration_by_teacher'
    )
