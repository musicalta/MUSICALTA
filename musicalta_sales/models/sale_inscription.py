import json
import datetime

from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleInscription(models.Model):
    _name = 'sale.inscription'
    _description = 'Sale Inscription'

    name = fields.Char(
        string='Name',
    )
    session_id = fields.Many2one(
        string='Session',
        comodel_name='event.event',
        required=True,
        domain = "[('stage_id.pipe_end', '!=', True)]",
    )
    sale_order_id = fields.Many2one(
        string='Order',
        comodel_name='sale.order',
    )
    pricelist_id = fields.Many2one(
        'product.pricelist',
        string='Pricelist',
        required=True,
    )
    teacher_ids = fields.Many2many(
        string='Professeurs',
        comodel_name='hr.employee',
        related='session_id.teacher_ids',
    )
    usual_teacher = fields.Char('Professeur habituel')
    musical_level_id = fields.Many2one(
        'musical.level',
        string='Niveau musical'
    )
    partition = fields.Char('Partition')
    available_product_ids = fields.Many2many(
        'product.product', 
        related='session_id.available_product_ids'
    )
    partner_id = fields.Many2one(
        'res.partner',
        required=True,
        string='Client',
    )
    is_adult = fields.Boolean(
        'Adulte',
        compute='_compute_is_adult',
    )
    product_pack_id = fields.Many2one(
        string='Pack',
        comodel_name='product.product',
        required=True,
        domain="['|',('is_product_for_adults_and_minors', '=', True),('is_product_for_adults', '=', is_adult),('pack_ok', '=', True), ('id', 'in', available_product_ids)]",
    )
    is_auditor = fields.Boolean(
        string='Auditeur',
        default=False,
    )
    product_hebergement_id = fields.Many2one(
        'product.product',
        string='Hébergement',
        domain="[('is_product_hebergement', '=', True), ('id', 'in', available_product_ids)]",
    )
    product_launch_id = fields.Many2one(
        'product.product',
        string='Repas',
        domain="[('is_product_launch', '=', True)]"
    )
    discipline_id_1 = fields.Many2one(
        'employee.discipline', 
        string='Discipline 1'
    )
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
    )
    product_work_room_domain_id = fields.Char(
        compute="_compute_product_work_room_domain_id",
        readonly=True,
        store=False,
    )

    tessiture_id = fields.Many2one('musical.tessiture', string='Tessiture')
    is_harpiste = fields.Boolean(
        'Harpe',
        compute="_compute_is_harpiste",
        store=True,
    )
    is_pianiste = fields.Boolean(
        'Piano',
        compute="_compute_is_pianiste",
        store=True,
    )
    is_harpiste_with_instruments = fields.Boolean("J'ai mon instrument")

    
    @api.onchange('product_pack_id')
    def _onchange_product_pack_id(self):
        if self.product_pack_id:
            self.product_hebergement_id = self.product_pack_id.pack_line_ids.filtered(lambda x: x.product_id.is_product_hebergement).product_id.id
    
    @api.onchange('discipline_id_1')
    def _onchange_discipline_id_1(self):
        if self.discipline_id_1:
            if self.teacher_id_1:
                self.teacher_id_1 = False

    @api.onchange('discipline_id_2')
    def _onchange_discipline_id_2(self):
        if self.discipline_id_2:
            if self.teacher_id_2:
                self.teacher_id_2 = False
    
    @api.depends('partner_id')
    def _compute_is_adult(self):
        for record in self:
            if record.partner_id.date_of_birth and record.session_id.date_begin:
                # Calculer l'âge à la date de la session
                age_at_session = relativedelta(record.session_id.date_begin, record.partner_id.date_of_birth).years
                record.is_adult = age_at_session >= 18
            else:
                record.is_adult = False
    
    @api.depends('discipline_id_1', 'discipline_id_2')
    def _compute_is_harpiste(self):
        for record in self:
            record.is_harpiste = record.discipline_id_1.is_harpe or record.discipline_id_2.is_harpe
    
    @api.depends('discipline_id_1', 'discipline_id_2')
    def _compute_is_pianiste(self):
        for record in self:
            record.is_pianiste = record.discipline_id_1.is_piano or record.discipline_id_2.is_piano
    
    @api.depends('discipline_id_1', 'discipline_id_2', 'is_harpiste_with_instruments')
    def _compute_product_work_room_domain_id(self):
        for rec in self:
            # Cas de base : utiliser tous les produits disponibles
            available_product_ids = self.available_product_ids.ids

            # # Vérification des disciplines spécifiques
            # if rec.discipline_id_1 or rec.discipline_id_2:
            #     available_product_ids = rec._get_discipline_specific_products()

            # if rec.is_harpiste_with_instruments:
            #     # Cas spécifique pour un harpiste avec instruments
            #     available_product_ids = rec._get_one_day_room_product_ids()

            # Construire le domaine JSON pour le champ product_work_room_domain_id
            rec.product_work_room_domain_id = json.dumps(
                [('is_work_rooms', '=', True), ('id', 'in', available_product_ids)]
            )

    def _get_discipline_specific_products(self):
        """
        Récupère les ID de produits associés aux disciplines spécifiques (harpe, piano).
        """
        available_product_ids = []
        for discipline_field in ['discipline_id_1', 'discipline_id_2']:
            discipline = getattr(self, discipline_field)
            if discipline and (discipline.is_harpe or discipline.is_piano):
                available_product_ids += discipline.product_work_room_ids.ids

        return available_product_ids if available_product_ids else self.available_product_ids.ids

    def _get_one_day_room_product_ids(self):
        """
        Récupère les ID de produits pour les salles de travail disponibles pour une journée.
        Spécifique aux harpistes avec instruments.
        """
        product_ids = self.env['product.product'].search([
            ('is_work_rooms', '=', True),
            ('is_one_day_room', '=', True),
        ])
        return product_ids.ids


        
    def action_open_sale_order(self):
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
        }
    
    def action_update_or_create(self):
        self._update_or_create({})
        return True
    
    @api.constrains('session_id', 'partner_id')
    def _check_session_partner(self):
        for record in self:
            sale_inscription = self.env['sale.inscription'].search([
                ('session_id', '=', record.session_id.id),
                ('partner_id', '=', record.partner_id.id),
                ('id', '!=', record.id),
            ])
            if sale_inscription:
                raise UserError(_('Cette personne est déjà inscrite à cette session'))

    def unlink(self):
        for record in self:
            record.sale_order_id.order_line.filtered(lambda x: x.inscription_id.id == record.id).unlink()
        return super(SaleInscription, self).unlink()
    
    def _update_or_create(self, vals):
        if self.sale_order_id:
            self.sale_order_id.order_line.filtered(lambda x: x.inscription_id.id == self.id).unlink()
            events_registrations_ids = self.env['event.registration'].search([
                ('inscription_id', '=', self.id),
            ])
            event_lunch_ids = self.env['event.lunch.order'].search([
                ('inscription_id', '=', self.id),
            ])
            event_lunch_ids.unlink()
            events_registrations_ids.unlink()
        return self.process_registration()
        
    def _find_or_create_sale(self):
        SaleOrder = self.env['sale.order']
        sale_order = SaleOrder.search([
            ('partner_id', '=', self.partner_id.id),
            ('state', '=', 'draft'),
            ('event_type_id', '=', self.session_id.event_type_id.id),
        ])
        if not sale_order:
            sale_order = SaleOrder.create({
                'partner_id': self.partner_id.id,
                'event_type_id': self.session_id.event_type_id.id,
            })
        self.sale_order_id = sale_order.id
        return sale_order

    def process_registration(self):
        #MÊME DEVIS POUR LA MÊME ACADÉMIE \ET POUR LE MÊME CLIENT#
        if not self.sale_order_id:
            sale_order = self._find_or_create_sale()
            self.name = 'Inscription' + '-' + self.partner_id.name + '-' + sale_order.name
        sale_order = self.sale_order_id
        self.sale_order_id.pricelist_id = self.pricelist_id.id
        sale_order_line = []
        event_registration = []
        if self.discipline_id_1 and self.teacher_id_1:
            if self.product_pack_id:
                event_ticket_id = self.env['event.event.ticket'].search([
                    ('event_id', '=', self.session_id.id),
                    ('teacher_id', '=', self.teacher_id_1.id),
                    ('discipline_id', '=', self.discipline_id_1.id),
                ])
                if not event_ticket_id:
                    raise UserError(_('No ticket found for this teacher and discipline'))
                sale_order_line.append({
                    'sequence': 0,
                    'order_id': sale_order.id,
                    'product_id': self.product_pack_id.id,
                    'price_unit': self.product_pack_id.list_price,
                    'inscription_id': self.id,
                    'event_ticket_id': event_ticket_id.id,
                    'name': self.product_pack_id.display_name + ' - ' + \
                        self.session_id.name + ' - ' + self.teacher_id_1.name,
                })
                event_registration.append({
                    'teacher_id': self.teacher_id_1.id,
                    'discipline_id': self.discipline_id_1.id,
                    'partner_id': sale_order.partner_id.id,
                    'event_id': self.session_id.id,
                    'event_ticket_id': event_ticket_id.id,
                    'sale_order_id': sale_order.id,
                    'inscription_id': self.id,
                })
        if self.discipline_id_2 and self.teacher_id_2:
            product_fees = self.env['product.product'].search([
                ('is_fees', '=', True),
            ])
            if not product_fees:
                raise UserError(_('No fees product found'))
            event_ticket_id = self.env['event.event.ticket'].search([
                    ('event_id', '=', self.session_id.id),
                    ('teacher_id', '=', self.teacher_id_2.id),
                    ('discipline_id', '=', self.discipline_id_2.id),
                ])
            sale_order_line.append({
                'sequence': 1,
                'order_id': sale_order.id,
                'product_id': product_fees.id,
                'inscription_id': self.id,
                'event_ticket_id': event_ticket_id.id,
                'name': product_fees.display_name + ' - ' + \
                    self.session_id.name + ' - ' + self.teacher_id_2.name,
            })
            event_registration.append({
                'teacher_id': self.teacher_id_2.id,
                'discipline_id': self.discipline_id_2.id,
                'partner_id': sale_order.partner_id.id,
                'event_id': self.session_id.id,
                'event_ticket_id': event_ticket_id.id,
                'sale_order_id': sale_order.id,
                'inscription_id': self.id,
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
                'inscription_id': self.id,
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
                'inscription_id': self.id,
            })
        if self.product_hebergement_id or self.product_launch_id:
            self._lunch_management(self.product_launch_id, self.product_hebergement_id , sale_order)
        if self.product_work_rooms_id:
            self._work_room_management(self.product_work_rooms_id, sale_order)
        self.env['sale.order.line'].create(sale_order_line)
        self.env['event.registration'].create(event_registration)
        self._discount_process()
        return True

    def _work_room_management(self, product_work_rooms_id, sale_order):
        self.env['sale.order.line'].create({
            'sequence': 2, # TODO: check if this is the right sequence
            'order_id': sale_order.id,
            'inscription_id': self.id,
            'product_id': product_work_rooms_id.id,
        })

    def _lunch_management(self, product_launch_id, product_hebergement_id, sale_order):
        lunch_order = []
        if self.product_launch_id:
            lunch_order.append({
                'student_id': sale_order.partner_id.id,
                'meal_product_id': product_launch_id.id,
                'meal_quantity': self.session_id.calculate_days() * product_launch_id.number_of_meal,
                'session_id': self.session_id.id,
                'inscription_id': self.id,
            })
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'inscription_id': self.id,
                'product_id': self.product_launch_id.id,
            })
        if self.product_hebergement_id:
            lunch_order.append({
                'student_id': sale_order.partner_id.id,
                'meal_product_id': product_hebergement_id.id,
                'meal_quantity': self.session_id.calculate_days() * product_hebergement_id.number_of_meal,
                'session_id': self.session_id.id,
                'inscription_id': self.id,
            })
        self.env['event.lunch.order'].create(lunch_order)

    def _family_discount_process(self):
        family_id = self.partner_id.family_id
        if family_id:
            sale_inscription = self.env['sale.inscription'].search([
                ('partner_id', '!=', self.partner_id.id),
                ('partner_id.family_id', '=', family_id.id),
                ('session_id.event_type_id', '=', self.session_id.event_type_id.id),
                ('id', '!=', self.id),
            ])
            if sale_inscription:
                sale_order = sale_inscription.mapped('sale_order_id')
                invoices = sale_order.mapped('invoice_ids')
                account_payment = self.env['account.payment'].search([
                    ('partner_id', 'in', family_id.member_ids.ids),
                    ('payment_type', '=', 'inbound'),
                ]).filtered(lambda x: x.reconciled_invoice_ids in invoices)
                if account_payment:
                    self.env['sale.order.line'].create({
                        'order_id': self.sale_order_id.id,
                        'product_id': self.session_id.event_type_id.product_familiy_affiliation_id.id,
                        'price_unit': -self.session_id.event_type_id.product_familiy_affiliation_id.list_price,
                    })
                # LA RÉDUCTION DOIT S'APPLIQUER SUR LES X INSCRIPTIONS DE LA MÊME FAMILLE
                for sale in sale_inscription:
                    sale.env['sale.order.line'].create({
                        'order_id': sale.sale_order_id.id,
                        'product_id': self.session_id.event_type_id.product_familiy_affiliation_id.id,
                        'price_unit': -self.session_id.event_type_id.product_familiy_affiliation_id.list_price,
                    })

    def _check_exist_discount_line(self):
        """
            Check if a discount line already exist
        """
        if self.sale_order_id:
            for line in self.sale_order_id.order_line:
                if line.product_id.product_tmpl_id == self.session_id.event_type_id.product_familiy_affiliation_id or \
                    line.product_id.product_tmpl_id == self.session_id.event_type_id.product_remise_multi_session_id:
                    return True
        return False
    
    def _discount_process(self):
        if not self._check_exist_discount_line():
            if self.session_id.event_type_id.product_familiy_affiliation_id:
                self._family_discount_process()
            if self.session_id.event_type_id.product_remise_multi_session_id:
                if self.env['sale.inscription'].search([
                    ('partner_id', '=', self.partner_id.id),
                    ('session_id.event_type_id', '=', self.session_id.event_type_id.id),
                    ('id', '!=', self.id),
                ]):
                    self.env['sale.order.line'].create({
                        'order_id': self.sale_order_id.id,
                        'product_id': self.session_id.event_type_id.product_remise_multi_session_id.id,
                        'price_unit': -self.session_id.event_type_id.product_remise_multi_session_id.list_price,
                    })
            return True
    