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
        related_product = self.env['product.product'].search([
            ('detailed_type', '=', 'event'),
            ('available_for_event', '=', True),
        ])
        if not related_product:
            raise ValidationError(_('You have no product of type "event" in your database. You must create one.'))
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
                # Pour chaque discipline du prof, et pour chaque produit de type event, on crée un ticket

                for discipline in teacher.discipline_ids:
                    for product in related_product:
                            value = {
                                'event_id': self.id,
                                'name': f"{self.name} - {teacher.name} - {discipline.name} - {product.name}",
                                'teacher_id': teacher.id,
                                'seats_max': teacher.student_count_max,
                                'discipline_id': discipline.id,
                                'product_id': product.id,
                            }
                            new_ticket = ticket_model.create(value)
                            updated_values = {
                                'price': new_ticket.price + teacher.additional_cost
                            }
                            new_ticket.update(updated_values)

        self.remove_old_ticket()
