from odoo import models, fields

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
    registration_count = fields.Integer('Inscription', compute='_compute_inscription_count')

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
            registration.registration_count = registration_count_data.get(registration.id, 0)
    
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