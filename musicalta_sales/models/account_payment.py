from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        if vals.get('payment_transaction_id'):
            payment_transaction = self.env['payment.transaction'].browse(
                vals['payment_transaction_id']
            )
            if payment_transaction and payment_transaction.sale_order_ids:
                vals.update(
                    {'sale_order_id': payment_transaction.sale_order_ids[0].id})
        return super(AccountPayment, self).create(vals)
