from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    inscription_id = fields.Many2one(
        'sale.inscription',
        string='Event Inscription',
    )
