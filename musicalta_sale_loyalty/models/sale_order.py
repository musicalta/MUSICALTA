from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_reward_values_discount(self, reward, coupon, **kwargs):
        self.ensure_one()
        reward_values = super(SaleOrder, self)._get_reward_values_discount(
            reward, coupon, **kwargs)

        # modify the 'name' in each reward value
        for value in reward_values:
            if value.get('product_uom_qty') != 0:
                value['name'] = _('Discount: %(desc)s',
                                  desc=reward.with_context(lang=self.partner_id.lang).description)

        return reward_values
