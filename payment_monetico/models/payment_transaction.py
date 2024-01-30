# coding: utf-8
from odoo import exceptions, models, _
import logging
from werkzeug import urls
import datetime
import hmac, hashlib
import json
import base64
from odoo.http import request
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


ThreeDSecureChallengeValue = [
    ('no_preference', 'No preference'),
    ('challenge_preferred', 'Authentication desired'),
    ('challenge_mandated', 'Systematic authentication requested'),
    ('no_challenge_requested', 'No authentication required'),
    ('no_challenge_requested_strong_authentication', 'No authentication requested type of exemption strong authentication'),
    ('no_challenge_requested_trusted_third_party', 'No authentication requested type of trusted third party exemption'),
    ('no_challenge_requested_risk_analysis', 'No authentication required type of exemption prior risk analysis done')
]

required_fields=['ThreeDSecureChallenge']
class MoneticoPaiement_Hmac():

    def getStringToSeal(self,sData):
        sChaineMAC = []
        for key in sorted(sData):
            if sData[key]!="" or key in required_fields:
                if key == 'MAC':
                    continue
                sChaineMAC.append('%s=%s' % (key, sData[key]))
        return '*'.join(sChaineMAC)

    def _getUsableKey(self, monetico_key):

        hexStrKey = monetico_key[0:38]
        hexFinal = monetico_key[38:40] + "00";

        cca0 = ord(hexFinal[0:1])

        if cca0 > 70 and cca0 < 97:
            hexStrKey += chr(cca0 - 23) + hexFinal[1:2]
        elif hexFinal[1:2] == "M":
            hexStrKey += hexFinal[0:1] + "0"
        else:
            hexStrKey += hexFinal[0:2]

        import encodings.hex_codec
        c = encodings.hex_codec.Codec()
        hexStrKey = c.decode(hexStrKey)[0]

        return hexStrKey

    def hmac_sha1(self, sKey, sData):

        HMAC = hmac.HMAC(sKey, None, hashlib.sha1)
        HMAC.update(sData.encode('iso8859-1'))
        return HMAC.hexdigest()

    def computeHMACSHA1(self, sData, monetico_key):
        _sUsableKey = self._getUsableKey(monetico_key)
        return self.hmac_sha1(_sUsableKey, sData)

    def bIsValidHmac(self, sChaine, sMAC, monetico_key):
        return self.computeHMACSHA1(sChaine, monetico_key) == sMAC.lower()



class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'


    Hmac = MoneticoPaiement_Hmac()

    def _get_ThreeDSecureChallenge(self):
        if self.provider_id.three_d_secure_challenge==False:
            return ''
        else:
            return self.provider_id.three_d_secure_challenge

    def _get_ThreeDSecureDebrayable(self,sThreeDSecureChallengeValue):
        if sThreeDSecureChallengeValue == 'no_preference':
            return '0'
        elif sThreeDSecureChallengeValue == 'challenge_preferred':
            return '0'
        elif sThreeDSecureChallengeValue == 'challenge_mandated':
            return '0'
        elif sThreeDSecureChallengeValue == 'no_challenge_requested':
            return '1'
        elif sThreeDSecureChallengeValue == 'no_challenge_requested_strong_authentication':
            return '1'
        elif sThreeDSecureChallengeValue == 'no_challenge_requested_risk_analysis':
            return '1'
        elif sThreeDSecureChallengeValue == 'no_challenge_requested_trusted_third_party':
            return '1'
        else:
            return '0'



    # --------------------------------------------------
    # FORM RELATED METHODS
    # --------------------------------------------------


    def _get_specific_rendering_values(self, processing_values):
        """ Override of payment to return monetico-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of acquirer-specific processing values
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != 'monetico':
            return res

        billing = {
            "name": self.partner_name,
            "email": self.partner_email,
            "addressLine1": self.partner_address,
            "city": self.partner_city,
            "postalCode": self.partner_zip,
            "country": self.partner_country_id.code
        }

        if self.env.user.has_group('sale.group_delivery_invoice_address'):
            order = request.website.sale_get_order()
            if order:
                shipping = {"name": self.partner_name,
                            "addressLine1": self.partner_address,
                            "city": self.partner_city,
                            "postalCode": self.partner_zip,
                            "country": self.partner_country_id.code
                            }

        else:
            shipping = ""

        client = {
            "name": self.partner_name,
            "email": self.partner_email,
            "addressLine1": self.partner_address,
            "city": self.partner_city,
            "postalCode": self.partner_zip,
            "country": self.partner_country_id.code
        }

        raw = {"billing": billing, "client": client}
        if shipping:
            raw.update({"shipping": shipping})
        rawContexteCommand = json.dumps(raw)
        utf8ContexteCommande = rawContexteCommand.encode('utf8')
        sContexteCommande = base64.b64encode(utf8ContexteCommande).decode()

        base_url = self.provider_id.get_base_url()
        sLangue = str(self.env['res.lang'].search([('code', '=', self.partner_lang)]).iso_code).upper()
        sTPE = self.provider_id.monetico_TPE
        sDate = datetime.datetime.now().strftime("%d/%m/%Y:%H:%M:%S")



        sMontant = str(round(processing_values['amount'], 2)) + self.currency_id.name
        sReference = processing_values['reference']
        sTexteLibre = 'Sale Order Number '
        sVersion = self.provider_id.monetico_version
        sCodeSociete = self.provider_id.monetico_societe
        sEmail = self.partner_email
        sUrlKo = urls.url_join(base_url, self.provider_id.monetico_url_retour_err)
        sUrlOk = urls.url_join(base_url, self.provider_id.monetico_url_retour_ok)
        sThreeDSecureChallenge = self._get_ThreeDSecureChallenge()
        sThreeDSecureDebrayable = self._get_ThreeDSecureDebrayable(sThreeDSecureChallenge)

        monetico_values = {
            # Payment terminal
            'TPE': sTPE,
            'societe': sCodeSociete,
            'lgue': sLangue,
            'version': sVersion,
            # Payment informations
            'reference': sReference,
            'date': sDate,
            'montant': sMontant,
            'contexte_commande': sContexteCommande,
            # Optional parameters
            'mail': sEmail,
            'texte-libre': sTexteLibre,
            'url_retour_ok': sUrlOk,
            'url_retour_err': sUrlKo,
            '3dsdebrayable': sThreeDSecureDebrayable,
            'ThreeDSecureChallenge': sThreeDSecureChallenge,

        }

        sChaineMAC = self.Hmac.getStringToSeal(monetico_values)
        monetico_values.update({
            'MAC': self.Hmac.computeHMACSHA1(sChaineMAC, self.provider_id.monetico_key),
            'texte_libre': sTexteLibre,
            'ThreeDSecureDebrayable': sThreeDSecureDebrayable,
        })

        monetico_values.update({'api_url': self.provider_id._monetico_get_api_url()})
        return monetico_values






    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """ Override of payment to find the transaction based on monetico data.

        :param str provider_code: The code of the provider that handled the transaction
        :param dict notification_data: The notification data sent by the provider
        :return: The transaction if found
        :rtype: recordset of `payment.transaction`
        :raise: ValidationError if inconsistent data were received
        :raise: ValidationError if the data match no transaction
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != 'monetico':
            return tx

        reference = notification_data.get('reference')
        if not reference:
            error_msg = _('Monetico: received data with missing reference (%s)') % (reference)
            _logger.info(error_msg)
            raise ValidationError(error_msg)
        tx = self.search([('reference', '=', reference), ('provider_code', '=', 'monetico')])

        if not tx:
            error_msg = (_('Monetico: received data for reference %s; no order found') % (reference))
            raise ValidationError(error_msg)
        elif len(tx) > 1:
            error_msg = (_('Monetico: received data for reference %s; multiple orders found') % (reference))
            raise ValidationError(error_msg)

        return tx

    def _process_notification_data(self, notification_data):
        """ Override of payment to process the transaction based on monetico data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider
        :return: None
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != 'monetico':
            return

        acquirer = self.provider_id

        sComputedMAC=self.Hmac.getStringToSeal(notification_data)


        if self.Hmac.bIsValidHmac(sComputedMAC, notification_data['MAC'], acquirer.monetico_key):

            if notification_data['code-retour'] == "Annulation":
                self._set_canceled()
            elif notification_data['code-retour'] == "payetest":
                self._set_done()
            elif notification_data['code-retour'] == "paiement":
                self._set_done()
            else:
                self._set_pending()
            sResult = "0"
        else:
            sResult = "1\n" + sComputedMAC

        return "Pragma: no-cache\nContent-type: text/plain\n\nversion=2\ncdr=" + sResult





    def _monetico_validate_data(self, notification_data):

        tx_sudo = self._get_tx_from_notification_data('monetico', notification_data)
        provider_sudo = tx_sudo.provider_id
        sComputedMAC=self.Hmac.getStringToSeal(notification_data)
        if self.Hmac.bIsValidHmac(sComputedMAC, notification_data['MAC'], provider_sudo.monetico_key):
            sResult = "0"
        else:
            sResult = "1\n" + sComputedMAC

        return "Pragma: no-cache\nContent-type: text/plain\n\nversion=2\ncdr=" + sResult






