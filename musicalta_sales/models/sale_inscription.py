import json
import datetime
from datetime import date

from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC


from odoo.tools import format_datetime, format_time

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class SaleInscription(models.Model):
    _name = 'sale.inscription'
    _description = 'Sale Inscription'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'avatar.mixin']

    name = fields.Char(
        string='Name',
    )

    active = fields.Boolean(string='Active', default=True)

    image_1920 = fields.Image(related='partner_id.image_1920')

    session_id = fields.Many2one(
        string='Session',
        comodel_name='event.event',
        required=True,
        domain="[('stage_id.pipe_end', '!=', True)]",
    )
    pricelist_id = fields.Many2one('product.pricelist', string='Pricelist')
    sale_order_id = fields.Many2one(
        string='Order',
        comodel_name='sale.order',
    )
    teacher_ids = fields.Many2many(
        string='Professeurs',
        comodel_name='hr.employee',
        related='session_id.teacher_ids',
    )
    discipline_ids = fields.Many2many(
        string='Disciplines',
        comodel_name='employee.discipline',
        compute='_compute_discipline_ids',
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
    date_of_birth = fields.Date(
        'Date de naissance',
        related='partner_id.date_of_birth',
    )
    date_of_arrival = fields.Datetime(
        'Date d\'arrivée',)
    date_of_departure = fields.Datetime(
        'Date de départ')
    is_adult = fields.Boolean(
        'Adulte',
        store=True,
        compute='_compute_is_adult',
    )
    partner_age = fields.Integer(
        'Age',
        store=True,
        compute='_compute_is_adult',
    )

    product_pack_id = fields.Many2one(
        string='Pack',
        comodel_name='product.product',
        domain="['|',('is_product_for_adults_and_minors', '=', True),('is_product_for_adults', '=', is_adult),('pack_ok', '=', True), ('id', 'in', available_product_ids)]",
    )
    product_hebergement_id = fields.Many2one(
        'product.product',
        string='Hébergement',
        domain="[('is_product_hebergement', '=', True), ('id', 'in', available_product_ids)]",
    )

    product_bedroom_id = fields.Many2one(
        'product.product',
        string='Chambres',
        domain="[('is_product_bedroom', '=', True), ('id', 'in', available_product_ids)]",
    )

    product_launch_id = fields.Many2one(
        'product.product',
        string='Repas',
        domain="[('is_product_launch', '=', True)]"
    )
    discipline_id_1 = fields.Many2one(
        'employee.discipline',
        string='Discipline 1',
        domain="[('id', 'in', discipline_ids)]"
    )
    teacher_id_1 = fields.Many2one(
        'hr.employee',
        string='Professeur 1',
        domain="[('discipline_ids', 'in', discipline_id_1), ('id', 'in', teacher_ids)]"
    )
    discipline_id_2 = fields.Many2one(
        'employee.discipline',
        string='Discipline 2',
        domain="[('id', 'in', discipline_ids)]"
    )
    teacher_id_2 = fields.Many2one(
        'hr.employee',
        string='Professeur 2',
        domain="[('discipline_ids', 'in', discipline_id_2), ('id', 'in', teacher_ids)]"
    )
    options_ids = fields.Many2many(
        'event.event.ticket',
        string='Options',
        domain="[('event_id', '=', session_id),('is_option', '=', True)]",
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

    folder_state = fields.Selection(string='Dossier', selection=[(
        'to_complete', 'A compléter'), ('completed', 'Complété'),])
    is_autorisation_exit = fields.Boolean("Autorisation sortie")
    is_autorisation_bar = fields.Boolean("Autorisation bar")
    sale_origin_id = fields.Many2one(
        'sale.inscription.origin', string='Provenance')
    sale_origin_display_description = fields.Boolean(
        "Is display origin description", related='sale_origin_id.is_ask_description')
    sale_origin_description = fields.Text(
        string="Description provenance")
    is_train_going = fields.Boolean("Train aller")
    is_train_return = fields.Boolean("Train retour")
    is_bus_going = fields.Boolean("Bus aller")
    is_bus_return = fields.Boolean("Bus retour")
    departure_location_outbound_id = fields.Many2one(
        'sale.inscription.location', string="Lieu de départ (aller)")
    arrival_location_outbound_id = fields.Many2one(
        'sale.inscription.location', string="Lieu d'arrivée (aller)")
    departure_location_return_id = fields.Many2one(
        'sale.inscription.location', string="Lieu de départ (retour)")
    arrival_location_return_id = fields.Many2one(
        'sale.inscription.location', string="Lieu d'arrivée (retour)")
    note = fields.Html('Notes', related='partner_id.comment', readonly=False)
    note_internal = fields.Text(
        'Note interne', related='partner_id.note_internal', readonly=False)
    note_kitchen = fields.Text(
        'Note cuisine', related='partner_id.note_kitchen', readonly=False)
    note_professor = fields.Text(
        'Note professeur', related='partner_id.note_professor', readonly=False)

    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        related='sale_order_id.currency_id',
    )

    invoice_ids = fields.Many2many(
        comodel_name='account.move',
        string="Invoices",
        store=True,
        compute='_get_invoiced')

    invoices_amount_residual = fields.Monetary(
        string='Reste à payer',
        compute='_compute_invoice_amount', store=True,
    )

    invoices_amount_total = fields.Monetary(
        string='Montant Total factures',
        compute='_compute_invoice_amount', store=True,
    )

    state = fields.Selection([
        ('unconfirmed', 'Non confirmé'),
        ('confirmed', 'Confirmé')
    ], string='Etat', compute='_compute_state', store=True)

    @api.depends('invoice_ids', 'sale_order_id', 'sale_order_id.account_payment_ids')
    def _compute_state(self):
        for record in self:
            if record.invoice_ids or record.sale_order_id and record.sale_order_id.account_payment_ids:
                record.state = 'confirmed'
            else:
                record.state = 'unconfirmed'

    @api.depends('invoice_ids', 'invoice_ids.amount_residual', 'invoice_ids.amount_total', 'sale_order_id.amount_total')
    def _compute_invoice_amount(self):
        for record in self:
            record.invoices_amount_residual = sum(
                invoice.amount_residual for invoice in record.invoice_ids) if record.invoice_ids else record.sale_order_id.amount_total if record.sale_order_id else False
            record.invoices_amount_total = sum(
                invoice.amount_total for invoice in record.invoice_ids)

    @api.depends('sale_order_id.order_line.invoice_lines')
    def _get_invoiced(self):
        # The invoice_ids are obtained thanks to the invoice lines of the SO
        # lines, and we also search for possible refunds created directly from
        # existing invoices. This is necessary since such a refund is not
        # directly linked to the SO.
        for inscription in self:
            invoices_from_sale = inscription.sale_order_id.order_line.invoice_lines.move_id.filtered(
                lambda r: r.move_type in ('out_invoice', 'out_refund'))
            invoices_from_search = self.env['account.move'].search(
                [('inscription_id', '=', inscription.id)])
            inscription.invoice_ids = invoices_from_sale | invoices_from_search

    @api.onchange('session_id')
    def _onchange_session_id(self):
        if self.session_id and not self.date_of_arrival and not self.date_of_departure:
            self.date_of_arrival = self.session_id.date_begin
            self.date_of_departure = self.session_id.date_end
        elif self.session_id and self.date_of_arrival and self.date_of_departure:
            self.date_of_arrival = self.session_id.date_begin
            self.date_of_departure = self.session_id.date_end
        else:
            self.date_of_arrival = False
            self.date_of_departure = False
        return {'domain': {'discipline_id': [('id', 'in', self.discipline_ids.ids)]}}

    @api.depends('session_id')
    def _compute_discipline_ids(self):
        for record in self:
            if record.session_id:
                teacher_ids = record.session_id.teacher_ids
                disciplines = self.env['employee.discipline']
                for teacher in teacher_ids:
                    disciplines |= teacher.discipline_ids
                record.discipline_ids = disciplines
            else:
                record.discipline_ids = self.env['employee.discipline'].browse([
                ])

    @api.onchange('product_pack_id')
    def _onchange_product_pack_id(self):
        if self.product_pack_id:
            self.product_hebergement_id = self.product_pack_id.pack_line_ids.filtered(
                lambda x: x.product_id.is_product_hebergement).product_id.id

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

    @api.onchange('partner_id')
    def _onchange_parnter_id(self):
        if self.partner_id and self.partner_id.comment:
            self.note = self.partner_id.comment

    @api.depends('partner_id', 'session_id.date_begin', 'partner_id.date_of_birth')
    def _compute_is_adult(self):
        for record in self:
            if record.partner_id.date_of_birth and record.session_id.date_begin:
                # Calculer l'âge à la date de la session
                age_at_session = relativedelta(
                    record.session_id.date_begin, record.partner_id.date_of_birth).years
                record.is_adult = age_at_session >= 18
                record.partner_age = age_at_session
            else:
                record.is_adult = False
                record.partner_age = 0

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
            if rec.discipline_id_1.is_piano or \
                rec.discipline_id_2.is_piano or \
                    rec.discipline_id_1.is_harpe or \
                rec.discipline_id_2.is_harpe:
                available_product_ids = rec._get_discipline_specific_products()

            if rec.is_harpiste_with_instruments:
                # Cas spécifique pour un harpiste avec instruments
                available_product_ids = rec._get_one_day_room_product_ids()

            # Construire le domaine JSON pour le champ product_work_room_domain_id
            rec.product_work_room_domain_id = json.dumps(
                [('is_work_rooms', '=', True), ('id', 'in', available_product_ids)]
            )

    def toggle_active(self):
        for record in self:
            if record.active == True and record.sale_order_id:
                record.sale_order_id._action_cancel()
                self.env['event.registration'].search([
                    ('sale_order_id', '=', record.sale_order_id.id),
                ]).unlink()
            record.active = not record.active

    def _get_discipline_specific_products(self):
        """
        Récupère les ID de produits associés aux disciplines spécifiques (harpe, piano).
        """
        ProductProduct = self.env['product.product']
        discipline_ids = []
        if self.discipline_id_1.is_piano:
            discipline_ids.append(self.discipline_id_1.id)
        if self.discipline_id_2.is_piano:
            discipline_ids.append(self.discipline_id_2.id)
        if self.discipline_id_1.is_harpe:
            discipline_ids.append(self.discipline_id_1.id)
        if self.discipline_id_2.is_harpe:
            discipline_ids.append(self.discipline_id_2.id)
        product_ids = ProductProduct.search([
            ('is_work_rooms', '=', True),
            ('discipline_id', 'in', discipline_ids),
        ])
        return product_ids.ids

    def _get_one_day_room_product_ids(self):
        """
        Récupère les ID de produits pour les salles de travail disponibles pour une journée.
        Spécifique aux harpistes avec instruments.
        """
        product_ids = self.env['product.product'].search([
            ('is_work_rooms', '=', True),
            ('is_one_day_room', '=', True),
            ('id', 'in', self.available_product_ids.ids)
        ])
        return product_ids.ids

    def _get_tz(self):
        # Finds the first valid timezone in his tz, his work hours tz,
        #  the company calendar tz or UTC and returns it as a string
        self.ensure_one()
        if self.partner_id.lang == 'fr_FR':
            return 'Europe/Paris'
        else:
            return 'UTC'

    def action_open_sale_order(self):
        return {
            'name': 'Sale Order',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'view_mode': 'form',
            'res_id': self.sale_order_id.id,
        }

    def action_view_invoice(self):
        invoices = self.mapped('invoice_ids')
        action = self.env['ir.actions.actions']._for_xml_id(
            'account.action_move_out_invoice_type')
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + \
                    [(state, view)
                     for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}

        context = {
            'default_move_type': 'out_invoice',
        }
        if len(self) == 1:
            context.update({
                'default_partner_id': self.sale_order_id.partner_id.id,
                'default_partner_shipping_id': self.sale_order_id.partner_shipping_id.id,
                'default_invoice_payment_term_id': self.sale_order_id.payment_term_id.id or self.sale_order_id.partner_id.property_payment_term_id.id or self.env['account.move'].default_get(['invoice_payment_term_id']).get('invoice_payment_term_id'),
                'default_invoice_origin': self.sale_order_id.name,
            })
        action['context'] = context
        return action

    def action_update_or_create(self):
        self._update_or_create({})
        # # we must find the activity teams concerned by the model
        # team_ids = self.env['mail.activity.team'].search([('res_model_ids', 'in', self.env.ref('musicalta_sales.model_sale_inscription').id)])
        # # for each activity team, we must create an activity
        # for team in team_ids:
        #     # we search for activity type
        #     if team.activity_type_id:
        #         self.env['mail.activity'].create({
        #             'activity_type_id': team.activity_type_id.id,
        #             'res_model_id': self.env.ref('musicalta_sales.model_sale_inscription').id,
        #             'res_model': 'sale.inscription',
        #             'res_id': self.id,
        #             'user_id': team.user_id.id,
        #             'team_id': team.id,
        #         })
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
                raise UserError(
                    _('Cette personne est déjà inscrite à cette session'))

    def unlink(self):
        for record in self:
            record.sale_order_id.order_line.filtered(
                lambda x: x.inscription_id.id == record.id).unlink()
        return super(SaleInscription, self).unlink()

    def _update_or_create(self, vals):
        if self.sale_order_id:
            self.sale_order_id.with_context(
                disable_cancel_warning=True).action_cancel()
            self.sale_order_id.action_draft()
            self.sale_order_id.order_line.filtered(
                lambda x: x.inscription_id.id == self.id).unlink()
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
        # MÊME DEVIS POUR LA MÊME ACADÉMIE \ET POUR LE MÊME CLIENT#
        if not self.product_pack_id:
            raise UserError(_('You must select a pack'))
        if not self.sale_order_id:
            sale_order = self._find_or_create_sale()
            self.name = 'Inscription' + '-' + self.partner_id.name + '-' + sale_order.name
        sale_order = self.sale_order_id
        if self.pricelist_id:
            sale_order.pricelist_id = self.pricelist_id.id
        update_context_pricelist = {
            'pricelist': self.pricelist_id.id,
        }
        self = self.with_context(**update_context_pricelist)
        sale_order_line = []
        event_registration = []
        additional_cost_product = self.env['product.product'].search([
            ('is_additional_cost', '=', True),
        ])
        if self.discipline_id_1 and self.teacher_id_1:
            if self.product_pack_id:
                product_pack = self.product_pack_id.with_context(
                    {'lang': self.partner_id.lang, 'partner_id': self.partner_id.id})
                event_ticket_id = self.env['event.event.ticket'].search([
                    ('event_id', '=', self.session_id.id),
                    ('teacher_id', '=', self.teacher_id_1.id),
                    ('discipline_id', '=', self.discipline_id_1.id),
                ])
                if not event_ticket_id:
                    raise UserError(
                        _('No ticket found for this teacher and discipline'))
                price = self.pricelist_id._get_product_price(
                    self.product_pack_id, 1)
                sale_order_line.append({
                    'sequence': 0,
                    'order_id': sale_order.id,
                    'product_id': self.product_pack_id.id,
                    'price_unit': price,
                    'inscription_id': self.id,
                    'event_ticket_id': event_ticket_id.id,
                    'name': product_pack.display_name + ' - ' +
                    self.session_id.name + ' - ' + self.teacher_id_1.name,
                })
                if self.teacher_id_1.additional_cost > 0:
                    sale_order_line.append({
                        'sequence': 1,
                        'order_id': sale_order.id,
                        'product_id': additional_cost_product.id,
                        'price_unit': self.teacher_id_1.additional_cost,
                        'inscription_id': self.id,
                        'name': additional_cost_product.display_name + ' - ' +
                        self.session_id.name + ' - ' + self.teacher_id_1.name,
                    })

                if event_ticket_id.seats_unconfirmed == event_ticket_id.seats_max or event_ticket_id.seats_unconfirmed > event_ticket_id.seats_max:
                    raise UserError(
                        _('No more seats available for this teacher and discipline : %s %s (max %s reached)' % (self.teacher_id_1.name, self.discipline_id_1.name, event_ticket_id.seats_max)))

                event_registration.append({
                    'teacher_id': self.teacher_id_1.id,
                    'discipline_id': self.discipline_id_1.id,
                    'partner_id': sale_order.partner_id.id,
                    'event_id': self.session_id.id,
                    'event_ticket_id': event_ticket_id.id,
                    'sale_order_id': sale_order.id,
                    'inscription_id': self.id,
                })
        else:
            if self.product_pack_id and self.product_pack_id.is_auditor:
                product_pack = self.product_pack_id.with_context(
                    {'lang': self.partner_id.lang, 'partner_id': self.partner_id.id})
                price = self.pricelist_id._get_product_price(
                    self.product_pack_id, 1)
                sale_order_line.append({
                    'sequence': 0,
                    'order_id': sale_order.id,
                    'product_id': self.product_pack_id.id,
                    'price_unit': price,
                    'inscription_id': self.id,
                    'name': product_pack.display_name + ' - ' +
                    self.session_id.name,
                })

        if self.discipline_id_2 and self.teacher_id_2:
            product_fees = self.env['product.product'].with_context({'lang': self.partner_id.lang, 'partner_id': self.partner_id.id}).search([
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
                'name': product_fees.display_name + ' - ' +
                self.session_id.name + ' - ' + self.teacher_id_2.name,
            })
            if self.teacher_id_2.additional_cost > 0:
                sale_order_line.append({
                    'sequence': 1,
                    'order_id': sale_order.id,
                    'product_id': additional_cost_product.id,
                    'price_unit': self.teacher_id_2.additional_cost,
                    'inscription_id': self.id,
                    'name': additional_cost_product.display_name + ' - ' +
                    self.session_id.name + ' - ' + self.teacher_id_2.name,
                })
            if event_ticket_id.seats_unconfirmed >= event_ticket_id.seats_max:
                raise UserError(
                    _('No more seats available for this teacher and discipline : %s %s (max %s reached)' % (self.teacher_id_2.name, self.discipline_id_2.name, event_ticket_id.seats_max)))

            event_registration.append({
                'teacher_id': self.teacher_id_2.id,
                'discipline_id': self.discipline_id_2.id,
                'partner_id': sale_order.partner_id.id,
                'event_id': self.session_id.id,
                'event_ticket_id': event_ticket_id.id,
                'sale_order_id': sale_order.id,
                'inscription_id': self.id,
            })
        if self.options_ids:
            self._option_management(
                sale_order, sale_order_line, event_registration)
        if self.product_hebergement_id or self.product_launch_id:
            self._lunch_management(
                self.product_launch_id, self.product_hebergement_id, sale_order)
        if self.product_work_rooms_id:
            self._work_room_management(self.product_work_rooms_id, sale_order)
        if self.product_bedroom_id:
            sale_order_line.append({
                'order_id': sale_order.id,
                'product_id': self.product_bedroom_id.id,
                'inscription_id': self.id,
            })
        self.env['sale.order.line'].create(sale_order_line)
        self.env['event.registration'].create(event_registration)
        self._discount_process()
        if self.musical_level_id or self.usual_teacher or self.partition or self.tessiture_id:
            self._update_contact_informations()
        self._extra_night_management()
        sale_order._compute_advance_payment()
        return True

    def _get_extra_night_line_name(self, arrival=False, departure=False):
        """
            Get extra night line name

        Args:
            arrival (bool, optional): determine if before session. Defaults to False.
            departure (bool, optional): determine if after session. Defaults to False.

        Returns:
            _type_: _description_
        """
        date_of_arrival = format_datetime(
            self.env, self.date_of_arrival, dt_format="short", lang_code=self.partner_id.lang)
        date_of_departure = format_datetime(
            self.env, self.date_of_departure, dt_format="short", lang_code=self.partner_id.lang)
        date_of_begin = format_datetime(
            self.env, self.session_id.date_begin, dt_format="short", lang_code=self.partner_id.lang)
        date_of_end = format_datetime(
            self.env, self.session_id.date_end, dt_format="short", lang_code=self.partner_id.lang)
        if arrival:
            return "\n%s %s %s" % (
                date_of_arrival.split(' ')[0],
                "-",
                date_of_begin.split(' ')[0],
            )
        if departure:
            return "\n%s %s %s" % (
                date_of_end.split(' ')[0],
                "-",
                date_of_departure.split(' ')[0],
            )

    def _extra_night_management(self):
        """
            Manage extra night
        """
        data = []
        product_id = self.env['product.product'].search([
            ('is_extra_night', '=', True),
        ])
        if self.date_of_arrival < self.session_id.date_begin:
            days_timedelta = self.session_id.date_begin - self.date_of_arrival
            price = self.pricelist_id._get_product_price(
                product_id, days_timedelta.days)
            data.append({
                'product_id': product_id.id,
                'name': product_id.display_name + self._get_extra_night_line_name(arrival=True),
                'product_uom_qty': days_timedelta.days,
                'order_id': self.sale_order_id.id,
                'price_unit': price,
            })
        if self.date_of_departure > self.session_id.date_end:
            days_timedelta = self.date_of_departure - self.session_id.date_end
            price = self.pricelist_id._get_product_price(
                product_id, days_timedelta.days)
            data.append({
                'product_id': product_id.id,
                'name': product_id.display_name + self._get_extra_night_line_name(departure=True),
                'product_uom_qty': days_timedelta.days,
                'price_unit': price,
                'order_id': self.sale_order_id.id,
            })
        self.env['sale.order.line'].create(data)

    def _update_contact_informations(self):
        self.ensure_one()
        to_update = {}
        if self.partner_id:
            if self.musical_level_id:
                to_update['musical_level_id'] = self.musical_level_id.id
            if self.usual_teacher:
                to_update['usual_teacher'] = self.usual_teacher
            if self.partition:
                to_update['partition'] = self.partition
            if self.tessiture_id:
                to_update['tessiture_id'] = self.tessiture_id.id
            self.partner_id.update(to_update)

    def _option_management(self, sale_order, sale_order_line, event_registration):
        """
            Create sale order line and event registration for options

        Args:
            sale_order (obj): sale order
            sale_order_line (dict): sale order line dict
            event_registration (dict): event registration dict

        Raises:
            UserError: No ticket found for this teacher and discipline
        """
        for option in self.options_ids:
            event_ticket_id = self.env['event.event.ticket'].search([
                ('event_id', '=', self.session_id.id),
                ('option_id', '=', option.option_id.id),
                ('teacher_id', '=', option.teacher_id.id),
                ('product_id', '=', option.product_id.id),
                ('is_option', '=', True),
            ])
            if not event_ticket_id:
                raise UserError(
                    _('No ticket found for this teacher and discipline'))
            sale_order_line.append({
                'name': option.product_id.display_name + ' - ' + option.teacher_id.name + ' - ' + option.option_id.name,
                'order_id': sale_order.id,
                'inscription_id': self.id,
                'product_id': event_ticket_id.product_id.id,
            })
            event_registration.append({
                'teacher_id': option.teacher_id.id,
                'option_id': option.option_id.id,
                'partner_id': sale_order.partner_id.id,
                'event_id': self.session_id.id,
                'event_ticket_id': event_ticket_id.id,
                'sale_order_id': sale_order.id,
                'inscription_id': self.id,
            })

    def _work_room_management(self, product_work_rooms_id, sale_order):
        """_summary_

        Args:
            product_work_rooms_id (_type_): _description_
            sale_order (_type_): _description_
        """
        kwargs = {}
        if self.discipline_id_1.is_piano or self.discipline_id_1.is_harpe:
            kwargs.update({
                'discipline_id': self.discipline_id_1.id,
            })
        elif self.discipline_id_2.is_piano or self.discipline_id_2.is_harpe:
            kwargs.update({
                'discipline_id': self.discipline_id_2.id,
            })
        price = self.pricelist_id._get_product_price(
            product_work_rooms_id, 1, **kwargs)
        self.env['sale.order.line'].create({
            'sequence': 2,  # TODO: check if this is the right sequence
            'order_id': sale_order.id,
            'price_unit': price,
            'inscription_id': self.id,
            'product_id': product_work_rooms_id.product_variant_id.id,
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
            self.env['sale.order.line'].create({
                'order_id': sale_order.id,
                'inscription_id': self.id,
                'product_id': self.product_hebergement_id.product_variant_id.id,
            })
        self.env['event.lunch.order'].create(lunch_order)

    def _family_discount_process(self):
        family_id = self.partner_id.family_id
        if family_id:
            sale_inscription = self.env['sale.inscription'].search([
                ('partner_id', '!=', self.partner_id.id),
                ('partner_id.family_id', '=', family_id.id),
                ('session_id.event_type_id', '=',
                 self.session_id.event_type_id.id),
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
                        'product_id': self.session_id.event_type_id.product_familiy_affiliation_id.product_variant_id.id,
                        'price_unit': -self.session_id.event_type_id.product_familiy_affiliation_id.list_price,
                    })
                # LA RÉDUCTION DOIT S'APPLIQUER SUR LES X INSCRIPTIONS DE LA MÊME FAMILLE
                for sale in sale_inscription:
                    sale.env['sale.order.line'].create({
                        'order_id': sale.sale_order_id.id,
                        'product_id': self.session_id.event_type_id.product_familiy_affiliation_id.product_variant_id.id,
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
                    ('session_id.event_type_id', '=',
                     self.session_id.event_type_id.id),
                    ('id', '!=', self.id),
                ]):
                    orders = self.env['sale.inscription'].search([
                        ('partner_id', '=', self.partner_id.id),
                        ('session_id.event_type_id', '=',
                         self.session_id.event_type_id.id),
                    ])
                    self.env['sale.order.line'].create({
                        'order_id': self.sale_order_id.id,
                        'product_id': self.session_id.event_type_id.product_remise_multi_session_id.product_variant_id.id,
                        'price_unit': -self.session_id.event_type_id.product_remise_multi_session_id.list_price,
                    })
            return True

    def _get_fields_to_check_before_order_update(self):
        return ['session_id', 'partner_id', 'date_order_arrival', 'date_of_departure', 'pricelist_id', 'product_pack_id', 'product_hebergement_id', 'product_bedroom_id', 'product_launch_id', 'discipline_id_1', 'teacher_id_1', 'discipline_id_2', 'teacher_id_2', 'options_ids', 'product_work_rooms_id']

    def write(self, vals):
        fields_to_check = self._get_fields_to_check_before_order_update()
        needs_action = any(field in vals for field in fields_to_check)

        result = super(SaleInscription, self).write(vals)

        if needs_action:
            for record in self:
                record.action_update_or_create()

        return result
