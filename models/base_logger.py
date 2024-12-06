import logging
from odoo import models, api
from threading import current_thread

_logger = logging.getLogger(__name__)

# Dictionary to track recursive calls per thread
_recursion_guard = {}

def get_active_settings(env):
    return env['debug.logger.settings'].sudo().search([('active', '=', True)], limit=1)


def is_logging_enabled(env):
    settings = get_active_settings(env)
    return settings and settings.enable_logging

def should_log_model(env, model_name):
    # Don't log operations on the settings model itself
    if model_name == 'debug.logger.settings':
        return False
        
    settings = get_active_settings(env)
    if not settings or not settings.model_ids:
        return True  # Log all models if none specifically selected
    return env['ir.model'].sudo().search([('model', '=', model_name)], limit=1).id in settings.model_ids.ids

def should_log_method(env, method_name):
    settings = get_active_settings(env)
    return settings and settings.should_log_method(method_name)

class BaseLogger(models.AbstractModel):
    _inherit = 'base'

    def _log_operation(self, operation, **kwargs):
        """Central logging method with recursion prevention"""
        thread_id = current_thread().ident
        if thread_id in _recursion_guard:
            return
        
        try:
            _recursion_guard[thread_id] = True
            settings = get_active_settings(self.env)
            
            if (is_logging_enabled(self.env) and 
                should_log_model(self.env, self._name) and 
                should_log_method(self.env, operation)):
                
                # Regular logging
                log_message = f"\n[{operation.upper()}] on {self._name}"
                for key, value in kwargs.items():
                    log_message += f"\n{key}: {value}"
                _logger.info(log_message)
                
                # Store entry if enabled
                if settings.store_entries and self._name != 'debug.logger.entry':
                    self.env['debug.logger.entry'].sudo().create({
                        'name': operation.upper(),
                        'model': self._name,
                        'data': str(kwargs)
                    })
                    
                    # Cleanup old entries if needed
                    settings.cleanup_old_entries()
        finally:
            del _recursion_guard[thread_id]

    @api.model_create_multi
    def create(self, vals_list):
        records = super(BaseLogger, self).create(vals_list)
        self._log_operation('create', vals_list=vals_list)
        return records

    def write(self, vals):
        result = super(BaseLogger, self).write(vals)
        self._log_operation('write', ids=self.ids, vals=vals)
        return result

    def unlink(self):
        self._log_operation('unlink', ids=self.ids)
        return super(BaseLogger, self).unlink()

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        result = super(BaseLogger, self).search(domain, offset=offset, limit=limit, order=order)
        self._log_operation('search', domain=domain, offset=offset, limit=limit, order=order)
        return result

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        result = super(BaseLogger, self).search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        self._log_operation('search_read', domain=domain, fields=fields)
        return result

    @staticmethod
    def track_method(method):
        """Decorator to log custom methods."""
        def wrapper(func):
            def wrapped(self, *args, **kwargs):
                self._log_operation(method, args=args, kwargs=kwargs)
                return func(self, *args, **kwargs)
            return wrapped
        return wrapper