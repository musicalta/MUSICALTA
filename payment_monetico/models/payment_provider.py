from odoo import api, fields, models

ThreeDSecureChallengeValue = [
    ('no_preference', 'No preference'),
    ('challenge_preferred', 'Authentication desired'),
    ('challenge_mandated', 'Systematic authentication requested'),
    ('no_challenge_requested', 'No authentication required'),
    ('no_challenge_requested_strong_authentication', 'No authentication requested type of exemption strong authentication'),
    ('no_challenge_requested_trusted_third_party', 'No authentication requested type of trusted third party exemption'),
    ('no_challenge_requested_risk_analysis', 'No authentication required type of exemption prior risk analysis done')
]


class PaymentProvider(models.Model):
    _inherit = 'payment.provider'


    code = fields.Selection(selection_add=[('monetico', 'Monetico')], ondelete={'monetico': 'set default'})
    monetico_key = fields.Char("MAC Key", size=40, help="Merchant security key",required_if_provider='monetico')
    monetico_version = fields.Char("Version", default='3.0', help="Version of the payment system used ",required_if_provider='monetico')
    monetico_TPE = fields.Char("TPE", size=7, help="Merchant’s virtual EPT number",required_if_provider='monetico')
    monetico_societe = fields.Char("Societe", help="Alphanumeric code to enable the merchant to use the same virtual EPT for different sites (separate configurations) relating to the same activity",required_if_provider='monetico')
    monetico_url_retour_ok = fields.Char("URL OK",default='/payment/status', help="URL with which the buyer goes back to the merchant’s website following an accepted payment.",required_if_provider='monetico')
    monetico_url_retour_err = fields.Char("URL ERROR",default='/', help="URL with which the buyer goes back to the merchant’s website following a declined Payment or by clicking on the “Quit” button",required_if_provider='monetico')
    three_d_secure_challenge = fields.Selection(ThreeDSecureChallengeValue, '3DSecure Challenge', default='no_preference',required_if_provider='monetico')

    @api.model
    def _get_payment_method_information(self):
        res = super()._get_payment_method_information()
        res['monetico'] = {'mode': 'unique', 'domain': [('type', '=', 'bank')]}
        return res


    def _monetico_get_api_url(self):
        """ Return the appropriate URL of the requested API for the acquirer state.

        Note: self.ensure_one()

        :param str api_key: The API whose URL to get: 'hosted_payment_page' or 'directlink'
        :return: The API URL
        :rtype: str
        """
        self.ensure_one()

        if self.state == 'enabled':
            url = 'https://p.monetico-services.com/paiement.cgi'
        else:  # 'test'
            url='https://p.monetico-services.com/test/paiement.cgi'

        return url
