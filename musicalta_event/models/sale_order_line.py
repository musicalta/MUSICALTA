from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
        related='event_ticket_id.teacher_id'
    )
    teacher_ids = fields.Many2many(
        related='event_id.teacher_ids'
    )

