from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'res.partner'

    date_of_birth = fields.Date(string='Date de naissance')
    old = fields.Integer(string='Age', compute='_compute_old', store=True)
    is_adult = fields.Boolean(string='Is Adult', compute='_compute_is_adult', store=True)
    email_2 = fields.Char(string='Email 2')
    email_3 = fields.Char(string='Email 3')
    phone_2 = fields.Char(string='Phone 2')
    lang_spoken_ids = fields.Many2many('res.lang', string='Lang Spoken')
    preferal_professor_id = fields.Many2one('res.partner', string='Professeur')
    speakings = fields.Char(string='Langues parlées')
    regular_teacher = fields.Char(string='Professeur régulier')
    gender = fields.Selection(
        string='Genre',
        selection=[
            ('nc', 'Non communiqué'),
            ('man', 'Homme'),
            ('female', 'Femme')
        ],
        default='nc',
    )
    piece_played = fields.Html(string='Pièce jouée')
    level = fields.Char(string='Niveau')
    range = fields.Char(string='Tessiture')
    nationality = fields.Char(string='Nationalité')
    school = fields.Char(string='Ecole')

    @api.depends('date_of_birth')
    def _compute_old(self):
        for record in self:
            if record.date_of_birth:
                dob = fields.Date.from_string(record.date_of_birth)
                now = fields.Date.today()
                age = relativedelta(now, dob).years
                record.old = age
            else:
                record.old = 0

    @api.depends('old')
    def _compute_is_adult(self):
        for record in self:
            if record.old >= 18:
                record.is_adult = True
            else:
                record.is_adult = False

    @api.model
    def create(self, vals):
        if 'ref' not in vals or vals['ref'] is False:
            vals['ref'] = self.env['ir.sequence'].next_by_code('res.partner.student.number')
        return super(Partner, self).create(vals)
