from odoo import models, fields

class ResFamily(models.Model):
    _name = 'res.family'
    _description = 'Family'

    name = fields.Char(string='Family Name', compute='_compute_family_name')
    member_ids = fields.One2many('res.partner', 'family_id', string='Family Members')

    def _compute_family_name(self):
        for record in self:
            # Exemple de calcul du nom de famille (à personnaliser selon vos besoins)
            if record.member_ids:
                record.name = record.member_ids.mapped('name')
            else:
                record.name = 'Family'