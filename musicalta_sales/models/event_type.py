from odoo import _, api, fields, models


class EventType(models.Model):
    _inherit = 'event.type'

    product_familiy_affiliation_id = fields.Many2one('product.template', string='Remise famille')
    product_remise_multi_session_id = fields.Many2one('product.template', string='Remise multi-session')