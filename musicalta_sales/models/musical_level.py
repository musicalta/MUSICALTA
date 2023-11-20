from odoo import models, fields

class MusicalLevel(models.Model):
    _name = 'musical.level'
    _description = 'Musical Level'

    name = fields.Char(string='Musical Level', required=True)
