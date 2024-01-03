# -*- coding: utf-8 -*-

from odoo import models, fields


class DocumentsTag(models.Model):
    _inherit = 'documents.tag'

    naming_pattern = fields.Char(
        "Format", help="Define the naming pattern for attachments\n You can use {partner_name} and {object_name}")
