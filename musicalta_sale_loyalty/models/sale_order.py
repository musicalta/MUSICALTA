from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    def _get_reward_values_discount(self, reward, coupon, **kwargs):
        # call super to get original behavior
        reward_values = super(SaleOrder, self)._get_reward_values_discount(
            reward, coupon, **kwargs)

        # modify the 'name' in each reward value
        for value in reward_values:
            if value.get('product_uom_qty') != 0:
                value['name'] = _('Discount: %s' % reward.description)

        return reward_values
