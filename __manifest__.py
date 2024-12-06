{
    'name': 'Debug Logger',
    'version': '1.0',
    'category': 'Tools',
    'summary': 'A module to log database operations for debugging',
    'author': 'Your Company',
    'depends': ['base'],
    "data": [
        "data/default_config.xml",
        "views/debug_logger_settings_views.xml",
        "security/ir.model.access.csv",
        "views/debug_logger_entry_views.xml",
    ],
    'installable': True,
    'application': False,
}
