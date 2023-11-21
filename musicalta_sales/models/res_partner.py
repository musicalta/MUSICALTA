from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    family_id = fields.Many2one('res.family', string='Family')
