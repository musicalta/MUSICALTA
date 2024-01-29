from odoo import _, api, fields, models


class MailActivityTeam(models.Model):
    _inherit = "mail.activity.team"

    activity_type_id = fields.Many2one(string='Activity Type for sale inscription', comodel_name='mail.activity.type')
