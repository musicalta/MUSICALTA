from odoo import models, fields

class MusicalTessiture(models.Model):
    _name = 'musical.tessiture'
    _description = 'Musical Tessiture'

    name = fields.Char(string='Tessiture', required=True)
