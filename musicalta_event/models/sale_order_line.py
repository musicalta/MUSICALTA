from odoo import fields, models, api


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
        related='event_ticket_id.teacher_id'
    )
