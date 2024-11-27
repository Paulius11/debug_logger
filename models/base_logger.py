import logging
from odoo import models, api

_logger = logging.getLogger(__name__)

def is_logging_enabled(env):
    return env['ir.config_parameter'].sudo().get_param('debug_logger.enable') == 'True'

def get_logged_methods(env):
    methods = env['ir.config_parameter'].sudo().get_param('debug_logger.methods')
    return methods.split(',') if methods else []

def get_logged_models(env):
    models = env['ir.config_parameter'].sudo().get_param('debug_logger.models')
    return models.split(',') if models and models != 'all' else None

class BaseLogger(models.AbstractModel):
    _inherit = 'base'

    @api.model_create_multi
    def create(self, vals_list):
        if is_logging_enabled(self.env):
            model_name = self._name
            logged_models = get_logged_models(self.env)
            logged_methods = get_logged_methods(self.env)

            if (not logged_models or model_name in logged_models) and 'create' in logged_methods:
                for vals in vals_list:
                    _logger.info(f"\n[CREATE] on {model_name}: {vals}")
        return super(BaseLogger, self).create(vals_list)

    def write(self, vals):
        if is_logging_enabled(self.env):
            model_name = self._name
            logged_models = get_logged_models(self.env)
            logged_methods = get_logged_methods(self.env)

            if (not logged_models or model_name in logged_models) and 'write' in logged_methods:
                _logger.info(f"\n[WRITE] on {model_name}: {self.ids} with {vals}")
        return super(BaseLogger, self).write(vals)

    def unlink(self):
        if is_logging_enabled(self.env):
            model_name = self._name
            logged_models = get_logged_models(self.env)
            logged_methods = get_logged_methods(self.env)

            if (not logged_models or model_name in logged_models) and 'unlink' in logged_methods:
                _logger.info(f"\n[UNLINK] on {model_name}: {self.ids}")
        return super(BaseLogger, self).unlink()

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        if is_logging_enabled(self.env):
            model_name = self._name
            logged_models = get_logged_models(self.env)
            logged_methods = get_logged_methods(self.env)

            if (not logged_models or model_name in logged_models) and 'search' in logged_methods:
                _logger.info(f"\n[SEARCH] on {model_name}: domain={domain}, offset={offset}, limit={limit}, order={order}")
        return super(BaseLogger, self).search(domain, offset=offset, limit=limit, order=order)

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        if is_logging_enabled(self.env):
            model_name = self._name
            logged_models = get_logged_models(self.env)
            logged_methods = get_logged_methods(self.env)

            if (not logged_models or model_name in logged_models) and 'search_read' in logged_methods:
                _logger.info(f"\n[SEARCH_READ] on {model_name}: domain={domain}, fields={fields}")
        return super(BaseLogger, self).search_read(domain, fields, offset, limit, order)

    @staticmethod
    def track_method(method):
        """Decorator to log custom methods."""
        def wrapper(func):
            def wrapped(self, *args, **kwargs):
                if is_logging_enabled(self.env):
                    _logger.info(f"\n[CALL] {func.__name__} on {self._name} with args={args}, kwargs={kwargs}")
                return func(self, *args, **kwargs)
            return wrapped
        return wrapper
