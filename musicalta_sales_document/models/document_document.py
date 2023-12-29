# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    @api.depends('tag_ids')
    def _updates_attachment_name(self):
        for record in self:
            object = self.env['sale.inscription'].search(
                [('files_directory_id', '=', record.folder_id.id)], limit=1)
            if record.tag_ids and object:
                naming_pattern = record.tag_ids.filtered(
                    lambda r: r.naming_pattern)[0].naming_pattern if record.tag_ids.filtered(
                    lambda r: r.naming_pattern)[0] else False
                if naming_pattern:
                    attachment_extension = record.name.rsplit('.', 1)
                    new_name = naming_pattern.replace(
                        '{object_name}', object.name).replace(
                        '{partner_name}', object.partner_id.name).replace(
                        ' ', '_')

                    record.name = new_name + "." + attachment_extension[1]

    def write(self, vals):
        tag_ids_updated = 'tag_ids' in vals
        res = super().write(vals)
        if tag_ids_updated:
            self._updates_attachment_name()
        return res
