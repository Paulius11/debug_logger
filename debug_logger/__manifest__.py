{
    'name': 'Debug Logger',
    'version': '17.0.1.1.1',
    'category': 'Tools',
    'website': 'https://github.com/Paulius11/debug_logger',
    'summary': 'A module to log database operations for debugging',
    'author': 'Paulius11',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'data/default_config.xml',
        'views/debug_logger_settings_views.xml',
        'views/debug_logger_entry_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}