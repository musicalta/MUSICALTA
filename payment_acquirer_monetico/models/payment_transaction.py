# -*- coding: utf-8 -*-
from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from decimal import *
import pytz
import datetime
from dateutil.relativedelta import relativedelta
import base64
import hashlib
import hmac
import encodings.hex_codec
import logging

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = 'payment.transaction'

    # Determines the display language of the payment page
    def _language_monetico_payment_page(self, partner_lang):
        try:
            monetico_lang = ["DE", "EN", "ES", "FR", "IT", "JA", "NL", "PT", "SV"]
            partner_lang = partner_lang[:2].upper()
            lang = "EN"
            if partner_lang in monetico_lang:
                lang = partner_lang

            return lang

        except Exception as e:
            _logger.info(f"language_monetico_payment_page : {e}")
            return False

    def _get_sale_order_addresses(self, sale_order_id):
        try:
            # Check if different delivery address
            match_billing_address = "false"
            if sale_order_id.partner_invoice_id == sale_order_id.partner_shipping_id:
                if sale_order_id.partner_invoice_id.street == sale_order_id.partner_shipping_id.street:
                    match_billing_address = "true"

            # Get billing information
            billing_firstname = sale_order_id.partner_invoice_id.firstname
            billing_lastname = sale_order_id.partner_invoice_id.lastname
            billing_address = sale_order_id.partner_invoice_id.street
            billing_city = sale_order_id.partner_invoice_id.city
            billing_zip = sale_order_id.partner_invoice_id.zip
            billing_country = sale_order_id.partner_invoice_id.country_id.code

            # Get shipping information
            shipping_firstname = sale_order_id.partner_shipping_id.firstname
            shipping_lastname = sale_order_id.partner_shipping_id.lastname
            shipping_address = sale_order_id.partner_shipping_id.street
            shipping_city = sale_order_id.partner_shipping_id.city
            shipping_zip = sale_order_id.partner_shipping_id.zip
            shipping_country = sale_order_id.partner_shipping_id.country_id.code
            shipping_email = f"\"{sale_order_id.partner_shipping_id.email}\""
            shipping_email = shipping_email if sale_order_id.partner_shipping_id.email != "" else "null"

            raw_command_context = """{
                "billing" : {
                   "firstName" : \"""" + billing_firstname + """\",
                   "lastName" : \"""" + billing_lastname + """\",
                   "addressLine1" : \"""" + billing_address + """\",
                   "city" : \"""" + billing_city + """\",
                   "postalCode" : \"""" + billing_zip + """\",
                   "country" : \"""" + billing_country + """\"
                },
                "shipping" : {
                   "firstName" : \"""" + shipping_firstname + """\",
                   "lastName" : \"""" + shipping_lastname + """\",
                   "addressLine1" : \"""" + shipping_address + """\",
                   "city" : \"""" + shipping_city + """\",
                   "postalCode" : \"""" + shipping_zip + """\",
                   "country" : \"""" + shipping_country + """\",
                   "email" : """ + shipping_email + """,
                   "matchBillingAddress" : """ + match_billing_address + """
                },
                "client" : {
                   "email" : """ + shipping_email + """
                }
            }"""
            import pdb; pdb.set_trace()
            utf8_command_context = raw_command_context.encode('utf8')
            command_context = base64.b64encode(utf8_command_context).decode()

            return command_context

        except Exception as e:
            _logger.info(f"_get_sale_order_addresses : {e}")
            return False

    def _get_invoice_addresses(self, invoice_id):
        try:
            # Check if different delivery address
            match_billing_address = "false"
            if invoice_id.partner_id == invoice_id.partner_shipping_id:
                if invoice_id.partner_id.street == invoice_id.partner_shipping_id.street:
                    match_billing_address = "true"

            # Get billing information
            billing_firstname = invoice_id.partner_id.name.split()[-1]
            billing_lastname = invoice_id.partner_id.name.split()[0]
            billing_address = invoice_id.partner_id.street
            billing_city = invoice_id.partner_id.city
            billing_zip = invoice_id.partner_id.zip
            billing_country = invoice_id.partner_id.country_id.code

            # Get shipping information
            shipping_firstname = invoice_id.partner_shipping_id.name.split()[-1]
            shipping_lastname = invoice_id.partner_shipping_id.name.split()[0]
            shipping_address = invoice_id.partner_shipping_id.street
            shipping_city = invoice_id.partner_shipping_id.city
            shipping_zip = invoice_id.partner_shipping_id.zip
            shipping_country = invoice_id.partner_shipping_id.country_id.code
            shipping_email = f"\"{invoice_id.partner_shipping_id.email}\""
            shipping_email = shipping_email if invoice_id.partner_shipping_id.email != "" else "null"

            raw_command_context = """{
                "billing" : {
                   "firstName" : \"""" + billing_firstname + """\",
                   "lastName" : \"""" + billing_lastname + """\",
                   "addressLine1" : \"""" + billing_address + """\",
                   "city" : \"""" + billing_city + """\",
                   "postalCode" : \"""" + billing_zip + """\",
                   "country" : \"""" + billing_country + """\"
                },
                "shipping" : {
                   "firstName" : \"""" + shipping_firstname + """\",
                   "lastName" : \"""" + shipping_lastname + """\",
                   "addressLine1" : \"""" + shipping_address + """\",
                   "city" : \"""" + shipping_city + """\",
                   "postalCode" : \"""" + shipping_zip + """\",
                   "country" : \"""" + shipping_country + """\",
                   "email" : """ + shipping_email + """,
                   "matchBillingAddress" : """ + match_billing_address + """
                },
                "client" : {
                   "email" : """ + shipping_email + """
                }
            }"""

            utf8_command_context = raw_command_context.encode('utf8')
            command_context = base64.b64encode(utf8_command_context).decode()

            return command_context

        except Exception as e:
            _logger.info(f"_get_invoice_addresses : {e}")
            return False

    def _generate_command_context(self):
        """
        The payment can come from a payment link on quote, on invoice or on the online store.
        Main sale can be retrieved differently in code
        :return: command context for signature
        """
        try:
            command_context = ""
            sale_order_id = self.env['sale.order'].browse(self.sale_order_ids.mapped('id'))
            invoice_id = self.env['account.move'].browse(self.invoice_ids.mapped('id'))
            if sale_order_id:
                # It's payment from website shop or payment link from sale order
                if len(sale_order_id) > 1:
                    raise ValidationError("Impossible de générer un lien de paiement sur plusieurs devis !")
                command_context = self._get_sale_order_addresses(sale_order_id)
            elif invoice_id:
                # It's a payment link from invoice
                if len(invoice_id) > 1:
                    raise ValidationError("Impossible de générer un lien de paiement sur plusieurs factures !")
                command_context = self._get_invoice_addresses(invoice_id)

            return command_context

        except Exception as e:
            _logger.info(f"_generate_command_context : {e}")
            return False

    def _compute_hmac_sha1(self, monetico_key, data_for_mac):
        return self.hmac_sha1(self._get_usable_key(monetico_key), data_for_mac)

    def hmac_sha1(self, hex_str_key, data_for_mac):
        mac_seal = hmac.HMAC(hex_str_key, None, hashlib.sha1)
        mac_seal.update(data_for_mac.encode('iso8859-1'))

        return mac_seal.hexdigest()

    # Permet de vérifier si le sceau MAC est cohérent
    def bIsValidHmac(self, monetico_key, sChaine, sMAC):
        return self._compute_hmac_sha1(monetico_key, sChaine) == sMAC.lower()

    def _get_usable_key(self, key_access):
        hex_str_key = key_access[0:38]
        hex_final = key_access[38:40] + "00"
        cca0 = ord(hex_final[0:1])

        if 70 < cca0 < 97:
            hex_str_key += chr(cca0 - 23) + hex_final[1:2]
        elif hex_final[1:2] == "M":
            hex_str_key += hex_final[0:1] + "0"
        else:
            hex_str_key += hex_final[0:2]

        c = encodings.hex_codec.Codec()
        hex_str_key = c.decode(hex_str_key)[0]

        return hex_str_key

    # Data to certify
    def _generate_mac_seal(self, data):
        try:
            data_for_mac = '*'.join([
                f"TPE={data['TPE']}",
                f"contexte_commande={data['command_context']}",
                f"date={data['date']}",
                f"dateech1={data['first_payment_date']}",
                f"dateech2={data['second_payment_date']}",
                f"dateech3={data['third_payment_date']}",
                f"dateech4={data['fourth_payment_date']}",
                f"lgue={data['lang']}",
                f"mail={data['mail']}",
                f"montant={data['amount']}",
                f"montantech1={data['first_amount_split']}",
                f"montantech2={data['second_amount_split']}",
                f"montantech3={data['third_amount_split']}",
                f"montantech4={data['fourth_amount_split']}",
                f"nbrech={data['number_of_splits']}",
                f"reference={data['reference']}",
                f"societe={data['company_code']}",
                f"texte-libre={data['comment']}",
                f"url_retour_err={data['return_error_url']}",
                f"url_retour_ok={data['return_url']}",
                f"version={data['version']}"
            ])

            return self._compute_hmac_sha1(self.provider_id.monetico_key, data_for_mac)

        except Exception as e:
            _logger.info(f"_generate_mac_seal : {e}")
            return False

    def _add_month_to_date(self, date, index):
        next_date = date + relativedelta(months=index)

        return next_date.strftime('%d/%m/%Y')

    # Split payment data
    def _generate_data_for_split_payment(self, amount_order, date_of_sale):
        try:
            payment_dates, amounts_split = [], []
            max_number_of_splits = 4
            number_of_splits = self.provider_id.monetico_number_of_splits

            # Calculation of date splits
            first_payment_date = date_of_sale.split(':')[0]
            first_payment_date_obj = datetime.datetime.strptime(first_payment_date, '%d/%m/%Y')

            # Addition of the first payment date
            payment_dates.append(first_payment_date)

            # We calculate the dates according to the rules of Monetico
            i = 1
            while i < int(number_of_splits):
                payment_dates.append(self._add_month_to_date(first_payment_date_obj, i))
                i += 1

            # Calculation of amounts splits (first payment with decimal and others)
            amount_split_order = Decimal(round(amount_order / int(number_of_splits)))
            amount_split_order = amount_split_order.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

            amount_first_split_order = amount_order - (amount_split_order * (int(number_of_splits) - 1))
            amounts_split.append(f"{amount_first_split_order}{self.currency_id.name}")

            while len(amounts_split) < int(number_of_splits):
                amounts_split.append(f"{amount_split_order}{self.currency_id.name}")

            # On ajoute dans tous les cas, 4 éléments dans le tableau pour traitement
            while len(payment_dates) < max_number_of_splits:
                payment_dates.append("")

            while len(amounts_split) < max_number_of_splits:
                amounts_split.append("")

            data = {
                'number_of_splits': number_of_splits,
                'first_payment_date': payment_dates[0],
                'second_payment_date': payment_dates[1],
                'third_payment_date': payment_dates[2],
                'fourth_payment_date': payment_dates[3],
                'first_amount_split': amounts_split[0],
                'second_amount_split': amounts_split[1],
                'third_amount_split': amounts_split[2],
                'fourth_amount_split': amounts_split[3],
            }

            return data

        except Exception as e:
            _logger.info(f"_generate_data_for_split_payment : {e}")
            return False

    def _get_specific_rendering_values(self, processing_values):
        try:
            res = super()._get_specific_rendering_values(processing_values)
            if self.provider_code not in ('monetico_standard', 'monetico_multi'):
                return res

            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            params = self.provider_id.get_params_in_file()

            amount_order = Decimal(self.amount)
            amount_order = amount_order.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

            api_url = self.provider_id.monetico_url
            version = params['version']
            monetico_ept = self.provider_id.monetico_ept
            date_of_sale = datetime.datetime.now(pytz.timezone('Europe/Paris')).strftime("%d/%m/%Y:%H:%M:%S")
            amount = f"{amount_order}{self.currency_id.name}"
            reference = self.reference
            return_url = f"{base_url}{self.provider_id.monetico_return_url}"
            return_error_url = f"{base_url}{self.provider_id.monetico_return_error_url}"
            lang = self._language_monetico_payment_page(self.partner_lang)
            company_code = self.provider_id.monetico_company_code
            command_context = self._generate_command_context()
            partner_email = self.partner_email
            comment = "Paiement depuis Odoo"

            data = {
                'api_url': api_url,
                'version': version,
                'TPE': monetico_ept,
                'date': date_of_sale,
                'amount': amount,
                'reference': reference,
                'return_url': return_url,
                'return_error_url': return_error_url,
                'lang': lang,
                'company_code': company_code,
                'command_context': command_context,
                'comment': comment,
                'mail': partner_email,
            }

            if self.provider_code == "monetico_multi":
                # processing of the split payment part
                monetico_multi_data = self._generate_data_for_split_payment(amount_order, date_of_sale)
                data.update(monetico_multi_data)
            else:
                data.update({
                    'number_of_splits': "",
                    'first_payment_date': "",
                    'second_payment_date': "",
                    'third_payment_date': "",
                    'fourth_payment_date': "",
                    'first_amount_split': "",
                    'second_amount_split': "",
                    'third_amount_split': "",
                    'fourth_amount_split': "",
                })

            data.update({
                'MAC': self._generate_mac_seal(data),
            })

            return data

        except Exception as e:
            _logger.info(f"_get_specific_rendering_values : {e}")
            return False

    # Vérifier que le montant et la référence correspondent au règlement d'une
    # commande enregistrée en attente de paiement
    @api.model
    def _get_tx_from_feedback_data(self, code, data):

        tx = super()._get_tx_from_feedback_data(code, data)
        providers_monetico = ['monetico_standard', 'monetico_multi']
        if code not in ['monetico_standard', 'monetico_multi']:
            return tx

        # Get transaction
        if 'reference' not in data:
            raise ValidationError("Monetico: " + _("No reference found in the return data"))

        reference = data['reference']
        tx = self.search([('reference', '=', reference), ('provider_code', 'in', providers_monetico)],
                         limit=1, order="id desc")
        if not tx:
            raise ValidationError("Monetico: " + _("No transaction found matching reference %s.", reference))

        return tx

    # Mets à jour le statut de la commande dans les bases de données
    def _process_feedback_data(self, data):

        super()._process_feedback_data(data)
        if self.provider_code not in ('monetico_standard', 'monetico_multi'):
            return

        # Get return code
        standard_success_return_code = ["payetest", "paiement"]
        standard_fail_return_code = ["Annulation"]

        multi_success_return_code = ["paiement_pf2", "paiement_pf3", "paiement_pf4"]
        multi_fail_return_code = ["Annulation_pf2", "Annulation_pf3", "Annulation_pf4"]

        # return data
        if 'code-retour' not in data:
            raise ValidationError("Monetico: " + _("No code-retour found in the return data"))
        status_code = data['code-retour']

        if status_code in standard_success_return_code or status_code in multi_success_return_code:
            status = "done"
            self._set_done()
        elif status_code in standard_fail_return_code or status_code in multi_fail_return_code:
            status = "cancel"
            msg = "Votre paiement a été annulé."
            self._set_error(msg)
        else:
            msg = f"Monetico: {status_code}"
            status = "error"
            _logger.warning(msg)
            self._set_error(msg)
        _logger.info(f"Monetico payment : reference: {self.reference} set as {status}.")
