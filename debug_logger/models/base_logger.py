import logging
import traceback
from odoo import models, api
from threading import current_thread

_logger = logging.getLogger(__name__)

# Dictionary to track recursive calls per thread
_recursion_guard = {}


def get_active_settings(env):
    """Get the currently active debug logger settings."""
    return env['debug.logger.settings'].sudo().search([('active', '=', True)], limit=1)


def is_logging_enabled(env):
    """Check if logging is globally enabled."""
    settings = get_active_settings(env)
    return settings and settings.enable_logging


def should_log_model(env, model_name):
    """Check if operations on this model should be logged."""
    # Don't log operations on the debug logger models themselves
    if model_name in ('debug.logger.settings', 'debug.logger.entry'):
        return False
        
    settings = get_active_settings(env)
    if not settings or not settings.model_ids:
        return True  # Log all models if none specifically selected
    return env['ir.model'].sudo().search([('model', '=', model_name)], limit=1).id in settings.model_ids.ids


def should_log_method(env, method_name):
    """Check if this method should be logged."""
    settings = get_active_settings(env)
    return settings and settings.should_log_method(method_name)


class BaseLogger(models.AbstractModel):
    _inherit = 'base'

    def _log_operation(self, operation, **kwargs):
        """
        Central logging method with recursion prevention.
        
        Args:
            operation (str): The operation being performed (create, write, unlink, etc.)
            **kwargs: Additional data to log
        """
        thread_id = current_thread().ident
        if thread_id in _recursion_guard:
            return
        
        try:
            _recursion_guard[thread_id] = True
            settings = get_active_settings(self.env)
            
            if (is_logging_enabled(self.env) and 
                should_log_model(self.env, self._name) and 
                should_log_method(self.env, operation)):
                
                # Get caller information for better debugging
                stack = traceback.extract_stack()
                caller_info = None
                for frame in reversed(stack):
                    if 'base_logger.py' not in frame.filename and 'odoo' in frame.filename:
                        caller_info = f"{frame.filename}:{frame.lineno} in {frame.name}()"
                        break
                
                # Enhanced logging with structured data
                log_data = {
                    'operation': operation.upper(),
                    'model': self._name,
                    'user_id': self.env.user.id,
                    'user_name': self.env.user.name,
                    'caller': caller_info or 'Unknown',
                    **kwargs
                }
                
                log_message = (
                    f"\n{'='*50} DEBUG LOGGER {'='*50}\n"
                    f"Operation: {operation.upper()}\n"
                    f"Model: {self._name}\n"
                    f"User: {self.env.user.name} (ID: {self.env.user.id})\n"
                    f"Called from: {caller_info or 'Unknown location'}\n"
                )
                
                for key, value in kwargs.items():
                    log_message += f"{key}: {value}\n"
                
                log_message += f"{'='*105}"
                
                _logger.info(log_message)
                
                # Store entry if enabled
                if settings.store_entries and self._name != 'debug.logger.entry':
                    try:
                        self.env['debug.logger.entry'].sudo().create({
                            'name': operation.upper(),
                            'model': self._name,
                            'data': str(log_data),
                            'caller_info': caller_info or 'Unknown',
                        })
                        
                        # Cleanup old entries if needed
                        settings.cleanup_old_entries()
                    except Exception as e:
                        _logger.warning(f"Failed to store debug log entry: {e}")
                        
        except Exception as e:
            _logger.error(f"Error in debug logger: {e}")
        finally:
            _recursion_guard.pop(thread_id, None)

    @api.model_create_multi
    def create(self, vals_list):
        """Override create to log creation operations."""
        records = super().create(vals_list)
        self._log_operation('create', 
                          vals_list=vals_list, 
                          record_ids=[r.id for r in records],
                          record_count=len(records))
        return records

    def write(self, vals):
        """Override write to log write operations."""
        old_values = {}
        if vals and is_logging_enabled(self.env):
            # Capture old values for comparison
            old_values = {
                record.id: {field: getattr(record, field) for field in vals.keys() if hasattr(record, field)}
                for record in self
            }
        
        result = super().write(vals)
        
        self._log_operation('write', 
                          ids=self.ids, 
                          vals=vals,
                          old_values=old_values,
                          record_count=len(self))
        return result

    def unlink(self):
        """Override unlink to log deletion operations."""
        record_data = []
        if is_logging_enabled(self.env):
            # Capture record data before deletion
            record_data = [
                {'id': record.id, 'display_name': getattr(record, 'display_name', str(record.id))}
                for record in self
            ]
        
        self._log_operation('unlink', 
                          ids=self.ids,
                          record_data=record_data,
                          record_count=len(self))
        return super().unlink()

    @api.model
    def search(self, domain, offset=0, limit=None, order=None):
        """Override search to log search operations."""
        result = super().search(domain, offset=offset, limit=limit, order=order)
        self._log_operation('search', 
                          domain=domain, 
                          offset=offset, 
                          limit=limit, 
                          order=order,
                          result_count=len(result))
        return result

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        """Override search_read to log search_read operations."""
        result = super().search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        self._log_operation('search_read', 
                          domain=domain, 
                          fields=fields, 
                          offset=offset, 
                          limit=limit, 
                          order=order,
                          result_count=len(result))
        return result

    @staticmethod
    def track_method(method_name):
        """
        Decorator to log custom methods.
        
        Usage:
            @BaseLogger.track_method('custom_operation')
            def my_custom_method(self):
                pass
        """
        def decorator(func):
            def wrapper(self, *args, **kwargs):
                result = func(self, *args, **kwargs)
                self._log_operation(method_name, args=args, kwargs=kwargs)
                return result
            return wrapper
        return decorator