from odoo import _, api, fields, models
from odoo.tools.misc import formatLang


class EventTicket(models.Model):
    _inherit = 'event.event.ticket'

    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
    )
    teacher_ids = fields.Many2many(
        related='event_id.teacher_ids'
    )
    discipline_ids = fields.Many2many(
        related='teacher_id.discipline_ids'
    )
    discipline_id = fields.Many2one(
        string='Discipline',
        comodel_name='employee.discipline',
        readonly=True
    )

    def name_get(self):
        """Adds ticket seats availability if requested by context."""
        if not self.env.context.get('name_with_seats_availability'):
            return super().name_get()
        res = []
        for ticket in self:
            if not ticket.seats_max:
                name = ticket.name
            elif not ticket.seats_available:
                name = _('%(ticket_name)s (%(discipline)s) (Sold out)', ticket_name=ticket.name,
                         discipline=ticket.discipline_id.name)
            else:
                name = _(
                    '%(ticket_name)s  (%(discipline)s) (%(count)s seats remaining)',
                    ticket_name=ticket.name,
                    discipline=ticket.discipline_id.name,
                    count=formatLang(self.env, ticket.seats_available, digits=0),
                )
            res.append((ticket.id, name))
        return res
