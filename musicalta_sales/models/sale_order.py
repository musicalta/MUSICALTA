from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_inscription_ids = fields.One2many(
        'sale.inscription',
        'sale_order_id',
        string='Event Inscriptions',
    )
    registration_count = fields.Integer('Inscription', compute='_compute_inscription_count')

    def action_open_event_inscription(self):
        return {
            'name': 'Event Registration',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.inscription',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_view_registration_list(self):
        return {
            'name': 'Event Registration',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.inscription',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', 'in', self.ids)],
        }

    def _compute_inscription_count(self):
        registration_data = self.env['sale.inscription']._read_group(
            [('sale_order_id', 'in', self.ids),],
            ['sale_order_id'], ['sale_order_id']
        )
        registration_count_data = {
            registration_data['sale_order_id'][0]:
            registration_data['sale_order_id_count']
            for registration_data in registration_data
        }
        for registration in self:
            registration.registration_count = registration_count_data.get(registration.id, 0)