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
    option_id = fields.Many2one(
        string='Option',
        comodel_name='employee.option',
    )
    is_option = fields.Boolean(
        string='Is option',
        default=False,
        related='product_id.is_option'
    )

    @api.onchange('teacher_id')
    def _onchange_teacher_id(self):
        return {
            'domain': {
                'discipline_id': [('id', 'in', self.teacher_id.discipline_ids.ids)],
                'option_id': [('id', 'in', self.teacher_id.options_ids.ids)]
            }
        }
