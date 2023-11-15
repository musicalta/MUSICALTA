# -*- coding: utf-8 -*-

from odoo import _, models, fields, api


class EventOption(models.Model):
    _name = 'event.option'

    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        required=True,
    )
    event_id = fields.Many2one(
        string='Event',
        comodel_name='event.event',
        required=True,
    )
    teacher_id = fields.Many2one(
        string='Teacher',
        comodel_name='hr.employee',
    )
    number_of_student = fields.Integer(
        string="Nombre d'élèves",
    )
    price = fields.Float('Prix')