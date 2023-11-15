from odoo import api, fields, models


class RegistrationEditorLine(models.TransientModel):
    _inherit = 'registration.editor.line'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
        related='sale_order_line_id.teacher_id'
    )

    def get_registration_data(self):
        self.ensure_one()
        return {
            'event_id': self.event_id.id,
            'event_ticket_id': self.event_ticket_id.id,
            'partner_id': self.editor_id.sale_order_id.partner_id.id,
            'name': self.name or self.editor_id.sale_order_id.partner_id.name,
            'phone': self.phone or self.editor_id.sale_order_id.partner_id.phone,
            'mobile': self.mobile or self.editor_id.sale_order_id.partner_id.mobile,
            'email': self.email or self.editor_id.sale_order_id.partner_id.email,
            'sale_order_id': self.editor_id.sale_order_id.id,
            'sale_order_line_id': self.sale_order_line_id.id,
            'teacher_id': self.sale_order_line_id.teacher_id.id
        }
