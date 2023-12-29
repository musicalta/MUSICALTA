from odoo import models, fields, api, _
import base64
from io import BytesIO
from zipfile import ZipFile


class DownloadAttachmentsWizard(models.TransientModel):
    _name = 'download.attachments.wizard'
    _description = 'Wizard to download attachments of sale inscriptions'

    tag_ids = fields.Many2many('documents.tag', string="Tags")
    sale_inscription_ids = fields.Many2many(
        'sale.inscription', string="Inscription_ids")

    def download_attachments(self):
        self.ensure_one()

        files_directory_ids = [
            record.files_directory_id.id for record in self.sale_inscription_ids]

        documents = self.env['documents.document'].search(
            [('folder_id', 'in', files_directory_ids), ('tag_ids', 'in', self.tag_ids.ids)]) if self.tag_ids else self.env['documents.document'].search(
            [('folder_id', 'in', files_directory_ids)])

        attachments = documents.mapped('attachment_id')
        zip_buffer = BytesIO()

        with ZipFile(zip_buffer, 'a') as zip_file:
            for attachment in attachments:
                file_name = attachment.name
                file_content = base64.b64decode(attachment.datas)
                zip_file.writestr(file_name, file_content)

        zip_buffer.seek(0)
        zip_data = zip_buffer.getvalue()
        zip_name = "attachments_%s.zip" % self.id

        return {
            'type': 'ir.actions.act_url',
            'url': '{}'.format(self.env['ir.attachment'].create({
                    'name': zip_name,
                    'type': 'binary',
                    'datas': base64.b64encode(zip_data),
                    'res_model': self._name,
                    'res_id': self.id,
            }).local_url),
            'target': 'self',
        }
