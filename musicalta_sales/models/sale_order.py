from odoo import models, fields

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def action_open_event_inscription(self):
        return {
            'name': 'Event Registration',
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.event.inscription',
            'view_mode': 'form',
            'target': 'new',
        }
