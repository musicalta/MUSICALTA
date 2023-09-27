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
    discipline_id = fields.Many2one(
        string='Discipline',
        comodel_name='employee.discipline',
        related='event_ticket_id.discipline_id'
    )

    @api.constrains('teacher_id')
    def _check_model(self):
        for record in self:
            if record.product_id.detailed_type == 'event' and not record.teacher_id:
                raise ValidationError(_('You have chosen an "event" type product. You must provide a teacher for this '
                                        'event.'))
