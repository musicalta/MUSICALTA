from odoo import api, fields, models

class HrEmployee(models.Model):
    _inherit = 'hr.employee'


    seats_limited = fields.Boolean(string='Seats limited', default=False)

    