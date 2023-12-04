# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions


class InheritedPaymentLinkWizard(models.TransientModel):
    _inherit = 'payment.link.wizard'

    monetico_access_payment = fields.Boolean(string="Monetico access payment", copy=False, store=False,
                                             compute="_get_monetico_access_value")

    @api.depends('res_id')
    def _get_monetico_access_value(self):
        for rec in self:
            monetico_access_payment = True
            if rec.res_model == "sale.order":
                order_id = rec.env['sale.order'].browse([rec.res_id])
                # Search if invoice and shipping address
                if not order_id.partner_invoice_id.street or not order_id.partner_invoice_id.zip \
                        or not order_id.partner_invoice_id.city or not order_id.partner_invoice_id.country_id:
                    monetico_access_payment = False
                if not order_id.partner_shipping_id.street or not order_id.partner_shipping_id.zip \
                        or not order_id.partner_shipping_id.city or not order_id.partner_shipping_id.country_id:
                    monetico_access_payment = False

            elif rec.res_model == "account.move":
                invoice_id = rec.env['account.move'].browse([rec.res_id])
                # Search if invoice and shipping address
                if not invoice_id.partner_id.street or not invoice_id.partner_id.zip \
                        or not invoice_id.partner_id.city or not invoice_id.partner_id.country_id:
                    monetico_access_payment = False
                if not invoice_id.partner_shipping_id.street or not invoice_id.partner_shipping_id.zip \
                        or not invoice_id.partner_shipping_id.city or not invoice_id.partner_shipping_id.country_id:
                    monetico_access_payment = False

            rec.monetico_access_payment = monetico_access_payment

