# -*- coding: utf-8 -*-
import logging
import pprint
from odoo import http
from odoo.http import request
_logger = logging.getLogger(__name__)


class MoneticoController(http.Controller):

    _url_cgi2='/payment/monetico/ipn'
    @http.route(_url_cgi2, type='http', auth='public', methods=['GET', 'POST'], csrf=False,save_session=False)
    def monetico_ipn(self, **post):
        """ Monetico IPN."""
        _logger.info('Monetico: entering handle_feedback_data with  data %s', pprint.pformat(post))
        if post:
            tx_sudo=request.env['payment.transaction'].sudo()
            tx_sudo._handle_notification_data('monetico',post)
            return tx_sudo._monetico_validate_data(post)
