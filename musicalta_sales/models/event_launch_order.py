from odoo import models, fields

class EventLunchOrder(models.Model):
    _name = 'event.lunch.order'
    _description = 'Lunch Order for Students'

    student_id = fields.Many2one('res.partner', string='Student', required=True)
    session_id = fields.Many2one('event.event', string='Session', required=True)
    meal_product_id = fields.Many2one('product.product', string='Meal Type', required=True)
    meal_quantity = fields.Integer(string='Number of Meals', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sale Order')
    inscription_id = fields.Many2one('sale.inscription', string='Inscription')