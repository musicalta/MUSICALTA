from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    inscription_id = fields.Many2one('sale.inscription', string='Inscription')

    def _synchronize_so_line_values(self, so_line):
        values = super()._synchronize_so_line_values(so_line)
        if not values.get('event_id'):
            sale_id = self.env['sale.order'].browse(
                values.get('sale_order_id')) or False
            if sale_id:
                values.update(
                    {'event_id': sale_id.event_inscription_ids[0].session_id.id if sale_id.event_inscription_ids.ids and sale_id.event_inscription_ids[0].session_id else False})
        return values
