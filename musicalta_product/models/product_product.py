from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_bundle = fields.Boolean(
        string='Is a bundle'
    )
    available_for_event = fields.Boolean(
        string='Available for event',
        help='If checked, this product will be available for events',
    )
    bundle_id = fields.Many2one(
        string='Is in bundle of',
        comodel_name='product.product',
        readonly=True,
    )
    product_bundle_ids = fields.One2many(
        string='Bundle products',
        comodel_name='product.product',
        inverse_name='bundle_id',
    )
    is_in_bundle = fields.Boolean(
        string='Is in product bundle',
        compute='_compute_is_in_bundle',
    )

    def _compute_is_in_bundle(self):
        bundles = self.search([('is_bundle', '=', True)])
        for record in self:
            record.is_in_bundle = False
            for bundle in bundles:
                if record.id in bundle.product_bundle_ids.ids:
                    record.is_in_bundle = True
