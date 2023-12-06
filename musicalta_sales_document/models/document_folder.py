# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class DocumentsFolder(models.Model):
    _inherit = 'documents.folder'
    _order = 'name'

    is_for_inscriptions_categories = fields.Boolean(
        string='Is for inscription categories ?')
