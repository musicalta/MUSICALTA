from odoo import _, models, fields, api


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_price_unit(self):
        for line in self:
            # check if there is already invoiced amount. if so, the price shouldn't change as it might have been
            # manually edited
            if line.qty_invoiced > 0:
                continue
            if not line.product_uom or not line.product_id or not line.order_id.pricelist_id:
                line.price_unit = 0.0
            elif line.product_id.is_bundle:
                price = 0
                for product in line.product_id.product_bundle_ids:
                    price += product.lst_price
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )
            else:
                price = line.with_company(line.company_id)._get_display_price()
                line.price_unit = line.product_id._get_tax_included_unit_price(
                    line.company_id,
                    line.order_id.currency_id,
                    line.order_id.date_order,
                    'sale',
                    fiscal_position=line.order_id.fiscal_position_id,
                    product_price_unit=price,
                    product_currency=line.currency_id
                )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(SaleOrderLine, self).create(vals_list)
        for record in res:
            if record.product_id.is_bundle:
                note_line_value = {
                    'display_type': 'line_note',
                    'order_id': record.order_id.id,
                    'name': ''
                }
                for bundle_product in record.product_id.product_bundle_ids:
                    note_line_value['name'] += _('Included {product} \n'.format(product=bundle_product.display_name))
                self.create([note_line_value])
