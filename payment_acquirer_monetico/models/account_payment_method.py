# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class AccountPaymentMethod(models.Model):
    _inherit = 'account.payment.method'

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['monetico_standard'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        res['monetico_multi'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}

        return res
