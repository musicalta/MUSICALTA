from odoo import models, fields


class SaleInscriptionOrigin(models.Model):
    _name = 'sale.inscription.origin'
    _description = 'Sale inscription origin'

    name = fields.Char(string='Provenance', required=True)
    is_ask_description = fields.Boolean(string='Demander la description')
