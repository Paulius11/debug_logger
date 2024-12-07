from odoo import models, fields, api

class DebugLoggerSettings(models.Model):
    _name = 'debug.logger.settings'
    _description = 'Debug Logger Settings'

    name = fields.Char(string='Name', required=True)
    active = fields.Boolean(default=True)
    enable_logging = fields.Boolean(string='Enable Logging', default=True)
    store_entries = fields.Boolean(string='Store Log Entries', default=True)
    max_entries = fields.Integer(string='Maximum Entries to Keep', default=1000,
                               help='Older entries will be automatically deleted')
    model_ids = fields.Many2many('ir.model', string='Models to Log',
                                help="Select models to log. If none selected, all models will be logged.")
    
    # Method selection fields
    log_create = fields.Boolean(string='Log Create Operations', default=True)
    log_write = fields.Boolean(string='Log Write Operations', default=True)
    log_unlink = fields.Boolean(string='Log Delete Operations', default=True)
    log_search = fields.Boolean(string='Log Search Operations', default=False)
    log_search_read = fields.Boolean(string='Log Search Read Operations', default=False)

    @api.model
    def get_current_settings(self):
        """Get active settings record"""
        return self.search([('active', '=', True)], limit=1)

    def activate_configuration(self):
        """Activate this configuration and deactivate others"""
        self.search([('id', '!=', self.id)]).write({'active': False})
        self.active = True
        return True

    def cleanup_old_entries(self):
        """Clean up old log entries based on max_entries setting"""
        if not self.store_entries or self.max_entries <= 0:
            return

        entries = self.env['debug.logger.entry'].search([], order='create_date desc')
        if len(entries) > self.max_entries:
            entries[self.max_entries:].unlink()

    def should_log_method(self, method_name):
        """Check if a specific method should be logged"""
        method_mapping = {
            'create': 'log_create',
            'write': 'log_write',
            'unlink': 'log_unlink',
            'search': 'log_search',
            'search_read': 'log_search_read',
        }
        return method_name in method_mapping and getattr(self, method_mapping[method_name])
