from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models, _


class SaleInscription(models.Model):
    _inherit = 'sale.inscription'

    files_directory_id = fields.Many2one(
        string='Directory for files', comodel_name='documents.folder', readonly=True)

    def action_see_documents(self):
        domain = [('folder_id', '=', self.files_directory_id.id)]
        return {
            'name': _('Documents'),
            'domain': domain,
            'res_model': 'documents.document',
            'type': 'ir.actions.act_window',
            'views': [(False, 'list'), (False, 'form')],
            'view_mode': 'tree,form',
            'context': "{'searchpanel_default_folder_id': %s}" % self.files_directory_id.id
        }

    def action_create_directory(self):
        directory_model = self.env['documents.folder']
        parent_folder = directory_model.search(
            [('is_for_inscriptions_categories', '=', True)], limit=1)
        for rec in self:
            directory_name = "%s - %s" % (rec.session_id.display_name,
                                          rec.partner_id.display_name)

            if bool(rec.session_id) and bool(rec.partner_id) and bool(parent_folder):

                partner_directory = directory_model.search(
                    [('name', '=', directory_name), ('parent_folder_id', '=', parent_folder.id)], limit=1)
                if bool(partner_directory) is False:
                    partner_directory = directory_model.create(
                        {'name': directory_name, 'parent_folder_id': parent_folder.id})

                rec.files_directory_id = partner_directory.id
