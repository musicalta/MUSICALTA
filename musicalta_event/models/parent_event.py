from odoo import api, fields, models

class EventParent(models.Model):
    _name = 'event.parent'
    _description = 'Parent Évènement'

    name = fields.Char(string='Nom', required=True)
    event_ids = fields.One2many('event.event', 'parent_id', string='Évènements')



