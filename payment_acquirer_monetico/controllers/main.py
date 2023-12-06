# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError

import pprint
import logging
_logger = logging.getLogger(__name__)


class PaymentAcquirerMonetico(http.Controller):
    _return_url = '/payment/monetico/return'
    _return_multi_payment_url = '/payment/moneticomulti/return'
    _success_url = '/payment/monetico/successful'
    _canceled_url = '/payment/monetico/canceled'

    @http.route(_return_url, type='http', auth='public', methods=['GET', 'POST'], csrf=False)
    def monetico_return_from_redirect(self, **kw):
        _logger.info("received notification data:\n%s", pprint.pformat(kw))
        validate_data = ""
        try:
            # We recover the payment intermediary thanks to the order reference
            payment_transaction_obj = http.request.env['payment.transaction']
            acquirer_id = payment_transaction_obj.sudo().search([('reference', '=', kw['reference'])], limit=1)
            provider = acquirer_id.acquirer_id.provider

            validate_data = self._monetico_validate_data(provider, **kw)
            try:
                if "cdr=0" in validate_data:
                    request.env['payment.transaction'].sudo()._handle_feedback_data(provider, kw)
            except ValidationError:
                pass

        except Exception as e:
            _logger.info(e)

        # Will we send an acknowledgment of receipt to the Monetico server
        return validate_data

    def _monetico_validate_data(self, provider, **kw):
        """
        Allows you to check the compliance of the data sent by Monetico
        :param kw: data returned by Monetico
        :return: acknowledgment of receipt to send to Monetico
        """
        result_confirm = "0"
        payment_acquirer_obj = http.request.env['payment.provider']

        tx_sudo = request.env['payment.transaction'].sudo()._get_tx_from_feedback_data(provider, kw)

        #  We check if a reference is present in the response of Monetico
        if not kw['reference']:
            _logger.warning("The reference is not present in the data received")
            return "Pragma: no-cache\nContent-type: text/plain\n\nversion=2\nMissing reference parameter"

        #  We check if a MAC seal is present in the response from Monetico
        if not kw['MAC']:
            _logger.warning("The MAC seal is not present in the data received")
            return "Pragma: no-cache\nContent-type: text/plain\n\nversion=2\nMissing MAC parameter"

        # We check the compliance of the MAC seal
        certification = []
        domain = [('provider', '=', provider)]
        for key, value in sorted(kw.items()):
            if key == 'MAC':
                continue
            certification.append(f"{key}={value}")
        data_for_mac = '*'.join(certification)

        monetico_key = payment_acquirer_obj.sudo().search(domain, limit=1).monetico_key
        result_mac = tx_sudo.bIsValidHmac(monetico_key, data_for_mac, kw['MAC'])

        # If this is not the case, we send a response to Monetico, otherwise we continue the treatment
        if not result_mac:
            result_confirm = "1\n" + data_for_mac
            _logger.warning("The seal does not match the data received")
            return f"Pragma: no-cache\nContent-type: text/plain\n\nversion=2\ncdr={result_confirm}"

        _logger.info('The data is validated')
        return f"Pragma: no-cache\nContent-type: text/plain\n\nversion=2\ncdr={result_confirm}"

    @http.route([_success_url, _canceled_url], type='http', methods=['GET', 'POST'], auth='public', csrf=False)
    def monetico_return(self, **kw):
        try:
            _logger.info("Datas %s", pprint.pformat(kw))
        except ValidationError:
            pass
        # return request.redirect('/shop/confirmation')
        return request.redirect('/payment/status')
