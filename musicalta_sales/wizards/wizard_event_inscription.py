import json
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardEventInscription(models.TransientModel):
    _name = 'wizard.event.inscription'
    _description = 'Event Registration Wizard'

    session_id = fields.Many2one(
        string='Session',
        comodel_name='event.event',
        domain = "[('stage_id.pipe_end', '!=', True)]",
    )
    teacher_ids = fields.Many2many(
        string='Professeurs',
        comodel_name='hr.employee',
        related='session_id.teacher_ids',
    )
    product_pack_id = fields.Many2one(
        string='Pack',
        comodel_name='product.product',
        domain=[('pack_ok', '=', True)],
    )
    is_auditor = fields.Boolean(
        string='Auditeur',
        default=False,
    )
    product_hebergement_id = fields.Many2one(
        'product.product',
        string='Hébergement',
        domain="[('is_product_hebergement', '=', True)]",
    )
    product_launch_id = fields.Many2one(
        'product.product',
        string='Repas',
        domain="[('is_product_launch', '=', True)]"
    )
    discipline_id_1 = fields.Many2one('employee.discipline', string='Discipline 1')
    teacher_id_1 = fields.Many2one(
        'hr.employee',
        string='Professeur 1',
        domain="[('discipline_ids', 'in', discipline_id_1), ('id', 'in', teacher_ids)]"
    )
    discipline_id_2 = fields.Many2one(
        'employee.discipline', 
        string='Discipline 2'
    )
    teacher_id_2 = fields.Many2one(
        'hr.employee',
        string='Professeur 2',
        domain="[('discipline_ids', 'in', discipline_id_2), ('id', 'in', teacher_ids)]"
    )
    options_ids = fields.Many2many(
        'event.event.ticket',
        string='Options',
        domain = "[('event_id', '=', session_id),('is_option', '=', True)]",
    )
    product_work_rooms_id = fields.Many2one(
        'product.product', 
        string='Salles de travail',
        domain = "[('is_work_rooms', '=', True)]",
    )
    
    @api.onchange('product_pack_id')
    def _onchange_product_pack_id(self):
        if self.product_pack_id:
            self.product_hebergement_id = self.product_pack_id.pack_line_ids.filtered(lambda x: x.product_id.is_product_hebergement).product_id.id
    
    @api.onchange('discipline_id_1')
    def _onchange_discipline_id_1(self):
        if self.discipline_id_1:
            self.product_work_rooms_id = self.env['product.product'].search([
                ('is_work_rooms', '=', True),
                ('discipline_id', '=', self.discipline_id_1.id),
            ],).id


    def process_registration(self):
        SaleOrder = self.env['sale.order']
        sale_order = SaleOrder.browse(self._context.get('active_id'))
        sale_order_line = []
        if self.product_pack_id:
            sale_order_line.append({
                'sequence': 0,
                'order_id': sale_order.id,
                'product_id': self.product_pack_id.id
            })
        event_registration = []
        pairs = []
        if self.discipline_id_1 and self.teacher_id_1:
            pairs.append((self.discipline_id_1, self.teacher_id_1))
        if self.discipline_id_2 and self.teacher_id_2:
            pairs.append((self.discipline_id_2, self.teacher_id_2))
            product_fees = self.env['product.product'].search([
                ('is_fees', '=', True),
            ])
            if not product_fees:
                raise UserError(_('No fees product found'))
            sale_order_line.append({
                'sequence': 1,
                'order_id': sale_order.id,
                'product_id': product_fees.id,
                'name': product_fees.display_name + ' - ' + \
                    self.session_id.name + ' - ' + self.teacher_id_2.name,
            })
        for discpline,teacher in pairs:
            event_ticket_id = self.env['event.event.ticket'].search([
                ('event_id', '=', self.session_id.id),
                ('teacher_id', '=', teacher.id),
                ('discipline_id', '=', discpline.id),
            ])
            if not event_ticket_id:
                raise UserError(_('No ticket found for this teacher and discipline'))

            event_registration.append({
                'teacher_id': teacher.id,
                'discipline_id': discpline.id,
                'partner_id': sale_order.partner_id.id,
                'event_id': self.session_id.id,
                'event_ticket_id': event_ticket_id.id,
                'sale_order_id': sale_order.id,
            })
        for option in self.options_ids:
            event_ticket_id = self.env['event.event.ticket'].search([
                ('event_id', '=', self.session_id.id),
                ('teacher_id', '=', option.teacher_id.id),
                ('discipline_id', '=', option.discipline_id.id),
                ('is_option', '=', True),
            ])
            if not event_ticket_id:
                raise UserError(_('No ticket found for this teacher and discipline'))
            sale_order_line.append({
                'order_id': sale_order.id,
                'product_id': event_ticket_id.product_id.id,
            })
            event_registration.append({
                'teacher_id': option.teacher_id.id,
                'discipline_id': option.discipline_id.id,
                'partner_id': sale_order.partner_id.id,
                'event_id': self.session_id.id,
                'event_ticket_id': option.id,
                'discipline_id': option.discipline_id.id,
                'sale_order_id': sale_order.id,
            })
        if self.product_hebergement_id or self.product_launch_id:
            meal_product_id = self.product_launch_id or self.product_hebergement_id
            self._lunch_management(meal_product_id, sale_order)
        if self.product_work_rooms_id:
            self._work_room_management(self.product_work_rooms_id, sale_order)
        self.env['sale.order.line'].create(sale_order_line)
        self.env['event.registration'].create(event_registration)
        return True

    def _work_room_management(self, product_work_rooms_id, sale_order):
        self.env['sale.order.line'].create({
            'sequence': 2, # TODO: check if this is the right sequence
            'order_id': sale_order.id,
            'product_id': product_work_rooms_id.id,
        })

    def _lunch_management(self, meal_product_id, sale_order):
        self.env['event.lunch.order'].create({
            'student_id': sale_order.partner_id.id,
            'meal_product_id': meal_product_id.id,
            'meal_quantity': self.session_id.calculate_days() * meal_product_id.number_of_meal,
            'session_id': self.session_id.id,
            # 'sale_order_id': sale_order.id,
        })
        if self.product_launch_id:
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'product_id': self.product_launch_id.id,
            })
    


class WizardEventInscriptionTraining(models.TransientModel):
    _name = "wizard.event.inscription.training"
    _description = "Event Registration Training Wizard"

    professor_id = fields.Many2one(
        string='Professor',
        comodel_name='hr.employee',
        required=True,
    )
    discipline_id = fields.Many2one(
        string='Discipline',
        comodel_name='employee.discipline',
        required=True,
    )
    wizard_id = fields.Many2one(
        'wizard.event.inscription',
        string='Wizard'
    )