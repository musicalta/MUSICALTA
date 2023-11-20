from odoo import _, fields, models, api
from odoo.exceptions import ValidationError


class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    inscription_id = fields.Many2one('sale.inscription', string='Inscription')

