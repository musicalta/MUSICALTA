# from odoo.addons.payment.tests.common import PaymentCommon
#
#
# class MoneticoCommon(PaymentCommon):
#
#     @classmethod
#     def setUpClass(cls, chart_template_ref=None):
#         super().setUpClass(chart_template_ref=chart_template_ref)
#
#         cls.buckaroo = cls._prepare_acquirer('buckaroo', update_values={
#             'buckaroo_website_key': 'dummy',
#             'buckaroo_secret_key': 'dummy',
#         })
#
#         # Override defaults
#         cls.acquirer = cls.buckaroo
#         cls.currency = cls.currency_euro
