from odoo import models, fields, api
from odoo.tools import float_compare


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    event_inscription_ids = fields.One2many(
        'sale.inscription',
        'sale_order_id',
        string='Event Inscriptions',
    )
    event_type_id = fields.Many2one(
        'event.type',
        string='Type d\'événement'
    )
    registration_count = fields.Integer(
        'Inscription', compute='_compute_inscription_count')
    inscription_note = fields.Html(
        string="Inscription Note", related='partner_id.comment', readonly=False)

    def action_open_event_inscription(self):
        return {
            'name': 'Event Registration',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.inscription',
            'view_mode': 'form',
            'target': 'new',
        }

    def action_view_registration_list(self):
        return {
            'name': 'Event Registration',
            'type': 'ir.actions.act_window',
            'res_model': 'sale.inscription',
            'view_mode': 'tree,form',
            'domain': [('sale_order_id', 'in', self.ids)],
        }

    def _compute_inscription_count(self):
        registration_data = self.env['sale.inscription']._read_group(
            [('sale_order_id', 'in', self.ids),],
            ['sale_order_id'], ['sale_order_id']
        )
        registration_count_data = {
            registration_data['sale_order_id'][0]:
            registration_data['sale_order_id_count']
            for registration_data in registration_data
        }
        for registration in self:
            registration.registration_count = registration_count_data.get(
                registration.id, 0)

    def _find_mail_template(self):
        """ Get the appropriate mail template for the current sales order based on its state.

        If the SO is confirmed, we return the mail template for the sale confirmation.
        Otherwise, we return the quotation email template.

        :return: The correct mail template based on the current status
        :rtype: record of `mail.template` or `None` if not found
        """
        res = super(SaleOrder, self)._find_mail_template()
        if self.env.context.get('proforma') or self.state not in ('sale', 'done'):
            return self.env.ref('musicalta_sales.mail_template_sale_inscription', raise_if_not_found=False)
        return res

    @api.depends(
        "currency_id",
        "company_id",
        "amount_total",
        "account_payment_ids",
        "account_payment_ids.state",
        "account_payment_ids.move_id",
        "account_payment_ids.move_id.line_ids",
        "account_payment_ids.move_id.line_ids.date",
        "account_payment_ids.move_id.line_ids.debit",
        "account_payment_ids.move_id.line_ids.credit",
        "account_payment_ids.move_id.line_ids.currency_id",
        "account_payment_ids.move_id.line_ids.amount_currency",
        "invoice_ids.amount_residual",
    )
    def _compute_advance_payment(self):
        super(SaleOrder, self)._compute_advance_payment()
        for order in self:
            mls = order.account_payment_ids.mapped("move_id.line_ids").filtered(
                lambda x: x.account_id.account_type == "asset_receivable"
                and x.parent_state == "posted"
            )
            advance_amount = 0.0
            for line in mls:
                line_currency = line.currency_id or line.company_id.currency_id
                # Exclude reconciled pre-payments amount because once reconciled
                # the pre-payment will reduce invoice residual amount like any
                # other payment.
                line_amount = line.balance
                line_amount *= -1
                if line_currency != order.currency_id:
                    advance_amount += line.currency_id._convert(
                        line_amount,
                        order.currency_id,
                        order.company_id,
                        line.date or fields.Date.today(),
                    )
                else:
                    advance_amount += line_amount
            # Consider payments in related invoices.
            invoice_paid_amount = 0.0
            for inv in order.invoice_ids.filtered(lambda x: x.payment_state != "reversed" and x.move_type != "out_refund"):
                invoice_paid_amount += inv.amount_total - inv.amount_residual
            amount_residual = order.amount_total - advance_amount
            payment_state = "not_paid"
            if mls:
                has_due_amount = float_compare(
                    amount_residual, 0.0, precision_rounding=order.currency_id.rounding
                )
                if has_due_amount <= 0:
                    payment_state = "paid"
                elif has_due_amount > 0:
                    payment_state = "partial"
            order.payment_line_ids = mls
            order.amount_residual = amount_residual
            order.advance_payment_status = payment_state

    def _get_confirmation_template(self):
        """ I remove the default confirmation template for the sale order
        """
        self.ensure_one()
        record = super(SaleOrder, self)._get_confirmation_template()
        return False

    def _create_invoices(self, grouped=False, final=False, date=None):
        moves = super(SaleOrder, self)._create_invoices(grouped, final, date)
        for move in moves:
            if move.line_ids.sale_line_ids.order_id.event_inscription_ids.ids:
                move.write(
                    {'inscription_id': move.line_ids.sale_line_ids.order_id.event_inscription_ids.ids[0]})
        return moves
