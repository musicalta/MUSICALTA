from odoo import models, fields


class SaleInscriptionLocation(models.Model):
    _name = 'sale.inscription.location'
    _description = 'Sale inscription location'

    name = fields.Char(string='Lieu', required=True)
