from odoo import api, fields, models


class EventTicket(models.Model):
    _inherit = 'event.event.ticket'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
    )
    discipline_id = fields.Many2one(
        string='Discipline',
        comodel_name='employee.discipline',
    )
    is_option = fields.Boolean(
        string='Is option',
        default=False,
    )

    @api.onchange('teacher_id')
    def _onchange_teacher_id(self):
        return {
            'domain': {
                'discipline_id': [('id', 'in', self.teacher_id.discipline_ids.ids)]
            }
        }
