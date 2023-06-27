from odoo import _, api, fields, models
from odoo.exceptions import UserError


class Event(models.Model):
    _inherit = 'event.event'

    teacher_ids = fields.Many2many(
        string='Teachers',
        comodel_name='hr.employee',
        relation='employee_event_rel_id',
        column1='employee_id',
        column2='event_id'
    )

    @api.model_create_multi
    def create(self, vals_list):
        res = super(Event, self).create(vals_list)
        for record in res:
            record.check_or_create_tickets()
        return res

    def write(self, vals):
        super(Event, self).write(vals)
        if vals.get('teacher_ids', False):
            self.check_or_create_tickets()

    def remove_old_ticket(self):
        for ticket in self.event_ticket_ids:
            teacher = ticket.teacher_id
            if teacher.id not in self.teacher_ids.ids:
                if ticket.seats_reserved or ticket.seats_unconfirmed:
                    raise UserError(_('You have deleted a teacher from the list of teachers available for this '
                                      'event, but there is already a registration for this event with this '
                                      'teacher.'))
                else:
                    ticket.unlink()

    def check_or_create_tickets(self):
        """After teachers update, we check if ticket is created for each teacher
        if no related ticket found, we create a new ticket for this event and teacher
        else we check if ticket already exist and we manage him (delete if necessary)
        """
        for teacher in self.teacher_ids:
            ticket_model = self.env['event.event.ticket']
            already_exist = ticket_model.search([
                ('event_id', '=', self.id),
                ('teacher_id', '=', teacher.id)], limit=1)
            if not already_exist:
                value = {
                    'event_id': self.id,
                    'name': f"{self.name} - {teacher.name}",
                    'teacher_id': teacher.id,
                    'seats_max': teacher.student_count_max
                }
                new_ticket = ticket_model.create(value)
                updated_values = {
                    'price': new_ticket.price + teacher.additional_cost
                }
                new_ticket.update(updated_values)
        self.remove_old_ticket()
