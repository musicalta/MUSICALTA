from odoo import api, fields, models


class EventType(models.Model):
    _inherit = 'event.type'

    limit_registration_by_teacher = fields.Boolean(
        string='Limit the number of registration according the student limit indicated on the teacher file',
        help="If this box is checked, the number of registrations is limited according to the maximum number of "
             "students indicated on the associated teacher's file"
    )
