from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    family_id = fields.Many2one('res.family', string='Family')

    usual_teacher = fields.Char('Professeur habituel')
    musical_level_id = fields.Many2one(
        'musical.level',
        string='Niveau musical'
    )
    partition = fields.Char('Partition')
    tessiture_id = fields.Many2one('musical.tessiture', string='Tessiture')
