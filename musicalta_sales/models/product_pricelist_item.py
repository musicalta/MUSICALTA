from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    discipline_id = fields.Many2one('employee.discipline', string='Discipline')