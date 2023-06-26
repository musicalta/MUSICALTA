from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
    )
    teacher_ids = fields.Many2many(
        related='event_id.teacher_ids'
    )

    @api.constrains('teacher_id')
    def _check_model(self):
        for record in self:
            if record.product_id.detailed_type == 'event' and not record.teacher_id:
                raise ValidationError(_('You choose an product with type "event" type. You must provide a teacher for '
                                        'this event'))
