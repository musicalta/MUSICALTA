from odoo import api, fields, models

class Event(models.Model):
    _inherit = 'event.event'

    parent_id = fields.Many2one('event.parent', string='Parent d\'Évènement')