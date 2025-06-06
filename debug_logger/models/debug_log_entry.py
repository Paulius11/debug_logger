from odoo import models, fields, api

class DebugLogEntry(models.Model):
    _name = 'debug.logger.entry'
    _description = 'Debug Logger Entry'
    _order = 'create_date desc'
    _rec_name = 'display_name'

    name = fields.Char(string='Operation', required=True, index=True)
    model = fields.Char(string='Model', required=True, index=True)
    user_id = fields.Many2one(
        'res.users', 
        string='User', 
        required=True, 
        default=lambda self: self.env.user,
        index=True
    )
    data = fields.Text(string='Operation Data')
    caller_info = fields.Char(string='Called From', help="File and line where the operation was called")
    display_name = fields.Char(string='Display Name', compute='_compute_display_name', store=True)

    @api.depends('name', 'model', 'create_date')
    def _compute_display_name(self):
        """Compute a meaningful display name for the log entry."""
        for record in self:
            record.display_name = f"{record.name} on {record.model} at {record.create_date}"