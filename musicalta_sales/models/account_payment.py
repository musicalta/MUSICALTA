from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        if vals.get('payment_transaction_id'):
            payment_transaction = self.env['payment.transaction'].browse(
                vals['payment_transaction_id']
            )
            if payment_transaction and payment_transaction.reference:
                sale_reference = ""
                if '-' in payment_transaction.reference:
                    sale_reference = payment_transaction.reference.split(
                        '-')[0]
                else:
                    sale_reference = payment_transaction.reference

                sale_order_id = self.env['sale.order'].search(
                    [('name', '=', sale_reference)], limit=1)
                if sale_order_id:
                    vals.update(
                        {'sale_id': sale_order_id.id})
        return super(AccountPayment, self).create(vals)
