from odoo import api, fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _get_applicable_rules_domain(self, products, date, **kwargs):
        res = super(ProductPricelist, self)._get_applicable_rules_domain(products, date, **kwargs)
        if kwargs.get('discipline_id'):
            res.append(('discipline_id', '=', kwargs.get('discipline_id')))
        return res