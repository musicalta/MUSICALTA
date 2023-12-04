# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions
from configparser import ConfigParser
import logging
import os

_logger = logging.getLogger(__name__)


class PaymentAcquirer(models.Model):
    _inherit = 'payment.acquirer'

    # Payment acquirer views parameters
    providers = [('monetico_standard', "Monetico - Standard payment"), ('monetico_multi', "Monetico - Multi payment")]
    on_delete = {'monetico_standard': 'set default', 'monetico_multi': 'set default'}

    provider = fields.Selection(selection_add=providers, ondelete=on_delete)
    monetico_key = fields.Char(string="Key",
                               help="The security key for synchronization with Monetico (40 hexadecimal characters)")
    monetico_ept = fields.Char(string="EPT Number",
                               help="Virtual EPT number for synchronization with Monetico (7 digit number)")
    monetico_company_code = fields.Char(string="Company code", help="Company code issued by Monetico")
    monetico_url = fields.Char(string="Gateway URL", help="Gateway url for synchronization with Monetico")
    monetico_return_url = fields.Char(string="Valid payment URL",
                                      help="Return URL in case of successful payment",
                                      readonly=True)
    monetico_return_error_url = fields.Char(string="Invalid payment URL",
                                            help="Return URL in case of Monetico processing error",
                                            readonly=True)
    monetico_cgi2_url = fields.Char(string="CGI2 URL", help="URL to send to Monetico")

    # For Monetico multi payment
    monetico_number_of_splits = fields.Selection(string="Number of payments",
                                                 selection=[('2', "2"), ('3', "3"), ('4', "4")],
                                                 ondelete='set default', help="Number of splits for orders")
    monetico_minimum_amount = fields.Char(string="Minimum amount", help="Minimum amount when paying in installments")

    @api.onchange('monetico_number_of_splits')
    def _onchange_pre_msg(self):
        self.ensure_one()
        monetico_number_of_splits = self.monetico_number_of_splits
        pre_msg = f"Vous pouvez payer en {monetico_number_of_splits} " \
                  f"fois avec Monetico après avoir cliqué sur le bouton de paiement."
        self.pre_msg = pre_msg

    @api.onchange('state')
    def _onchange_gateway_url(self):
        self.ensure_one()
        self.monetico_url = "https://p.monetico-services.com/test/paiement.cgi"
        if self.state == 'enabled':
            self.monetico_url = 'https://p.monetico-services.com/paiement.cgi'

    @api.onchange('state')
    def _onchange_cgi2_url(self):
        self.ensure_one()
        base_url = self.env['ir.config_parameter'].get_param('web.base.url')
        if base_url[-1] == "/":
            base_url = base_url[:-1]
        self.monetico_cgi2_url = f"{base_url}/payment/monetico/return"

    def monetico_get_form_action_url(self):
        print(self.monetico_url)

        return self.monetico_url

    def _get_default_payment_method_id(self):
        self.ensure_one()
        if self.provider == "monetico_standard":
            return self.env.ref('payment_acquirer_monetico.payment_method_monetico_standard').id
        elif self.provider == "monetico_multi":
            return self.env.ref('payment_acquirer_monetico.payment_method_monetico_multi').id
        else:
            return super()._get_default_payment_method_id()

    # Get default values of configuration file parameters
    def get_params_in_file(self):
        parameters = {}
        config = ConfigParser()
        folder = os.path.dirname(os.path.realpath(__file__))
        folder = folder.replace("/models", "")
        file_cfg = os.path.abspath(folder + "/config/config.cfg")
        config.read(file_cfg)
        for key, value in config.items('DEFAULT'):
            parameters[key] = value

        return parameters
