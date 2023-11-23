from odoo import api, fields, models


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    inscription_id = fields.Many2one('sale.inscription', string='Inscription')