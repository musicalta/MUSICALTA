from odoo import api, fields, models


class EventConfigurator(models.TransientModel):
    _inherit = 'event.event.configurator'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
    )
    teacher_ids = fields.Many2many(
        related='event_id.teacher_ids'
    )
