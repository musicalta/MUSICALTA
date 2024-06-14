from odoo import models, fields, api


class EventInscriptionBadgeProf(models.AbstractModel):
    _name = 'report.musicalta_sales.event_inscription_badge_prof'
    _description = 'Session Prof Badge Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = self.env['event.event'].browse(docids)

        report_data = []

        for event in docs:
            employees = event.teacher_ids | event.options_event_ticket_id.mapped(
                'teacher_id')
            for emp in employees:
                badges = event.teacher_ids.filtered(
                    lambda x: x.id == emp.id)
                options = event.options_event_ticket_id.filtered(
                    lambda x: x.teacher_id.id == emp.id)

                disciplines = badges.mapped('discipline_ids')
                options = options.mapped('option_id')

                report_data.append({
                    'session': event,
                    'employee': emp,
                    'disciplines': disciplines,
                    'options': options,
                })

        return {
            'doc_ids': docids,
            'doc_model': 'event.event',
            'docs': docs,
            'data': data,
            'report_data': report_data,
        }
