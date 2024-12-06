from odoo import models, fields

class DebugLogEntry(models.Model):
    _name = 'debug.logger.entry'
    _description = 'Debug Logger Entry'
    _order = 'create_date desc'

    name = fields.Char(string='Operation', required=True)
    model = fields.Char(string='Model', required=True)
    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user)
    data = fields.Text(string='Operation Data')