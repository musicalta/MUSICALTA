
from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    professor_id = fields.Many2one('hr.employee', string='Professeur')
    is_product_hebergement = fields.Boolean('Hébergement')
    is_product_launch = fields.Boolean('Repas')
    hebergement_product_id = fields.Many2one(
        "product.product",
        string="Hébergement",
        domain="[('is_product_hebergement', '!=', False)]",
    )
    number_of_meal = fields.Integer(
        string='Nombre de repas',
        default=0,
    )
    is_work_rooms = fields.Boolean('Salles de travail')
    discipline_id = fields.Many2one('employee.discipline', string='Discipline')
    is_fees = fields.Boolean('Frais')

    @api.onchange('professor_id')
    def _onchange_professor_id(self):
        for record in self:
            if record.professor_id:
                if record.name:
                    record.name = record.name + ' - ' + record.professor_id.name
                else:
                    record.name = record.professor_id.name
            else:
                record.name = False
    