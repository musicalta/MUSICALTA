from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class Event(models.Model):
    _inherit = 'event.event'

    teacher_ids = fields.Many2many(
        string='Teachers',
        comodel_name='hr.employee',
        relation='employee_event_rel_id',
        column1='employee_id',
        column2='event_id'
    )
    event_options_ids = fields.One2many(
        'event.option',
        'event_id',
        string='Event Options'
    )
    event_mail_teacher_ids = fields.One2many(
        'event.mail.teacher',
        'event_id',
        string='Event teachers mail'
    )
    options_event_ticket_id = fields.One2many(
        'event.event.ticket',
        'event_id',
        string='string',
        domain=[('is_option', '=', True)]
    )
    available_product_ids = fields.Many2many(
        'product.product',
        string='Available Products',
    )

    def get_teacher_participants(self, teacher_id):
        event_registration = self.registration_ids.filtered(
            lambda registration: registration.teacher_id.id == teacher_id)
        return event_registration.mapped('partner_id')

    def get_teacher_options(self, teacher_id):
        teacher_option_ids = self.options_event_ticket_id.filtered(
            lambda option: option.teacher_id.id == teacher_id)
        return teacher_option_ids

    def get_teacher_options_participants(self, teacher_id, option_id):
        options = self.registration_ids.filtered(
            lambda registration: registration.teacher_id.id == teacher_id and registration.option_id.id == option_id)
        return options.mapped('partner_id')

    def action_view_tickets(self):
        self.ensure_one()
        view_id = self.env.ref(
            'musicalta_event.event_event_ticket_tree_view').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tickets',
            'res_model': 'event.event.ticket',
            'views': [(view_id, 'tree')],
            'domain': [('event_id', '=', self.id), ('is_option', '=', False)],
            'context': {'default_event_id': self.id},
        }

    def action_view_event_options(self):
        self.ensure_one()
        view_id = self.env.ref(
            'musicalta_event.event_event_ticket_tree_view_options').id
        return {
            'type': 'ir.actions.act_window',
            'name': 'Options',
            'res_model': 'event.event.ticket',
            'views': [(view_id, 'tree')],
            'domain': [
                ('event_id', '=', self.id),
                ('is_option', '=', True)
            ],
            'context': {'default_event_id': self.id},
        }

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
                ('teacher_id', '=', teacher.id),
                ('discipline_id.id', 'in', teacher.discipline_ids.ids)], limit=1)
            if not already_exist:
                if not teacher.discipline_ids:
                    raise ValidationError(
                        _('Selected teacher have no discipline registred. You must fill a discpline for this teacher '
                          '"{teacher}"'.format(teacher=teacher.name)))
                for discipline in teacher.discipline_ids:
                    value = {
                        'event_id': self.id,
                        'name': f"{self.name} - {teacher.name}",
                        'teacher_id': teacher.id,
                        'seats_max': teacher.student_count_max,
                        'discipline_id': discipline.id
                    }
                    new_ticket = ticket_model.create(value)
                    updated_values = {
                        'price': new_ticket.price + teacher.additional_cost
                    }
                    new_ticket.update(updated_values)

        self.remove_old_ticket()

    def calculate_days(self):
        self.ensure_one()
        if self.date_begin and self.date_end:
            date_begin = fields.Datetime.from_string(self.date_begin)
            date_end = fields.Datetime.from_string(self.date_end)
            return (date_end - date_begin).days
        return 0
