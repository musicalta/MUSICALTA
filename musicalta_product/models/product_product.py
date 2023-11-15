from odoo import api, fields, models

class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _name_get(self):
        result = super(ProductProduct, self)._name_get()
        for product in self:
            if product.discipline_id:
                result[product.id] += ' - ' + product.discipline_id.name
        return result