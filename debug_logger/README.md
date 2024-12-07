A powerful debugging tool for Odoo that logs database operations and helps track down issues in your custom modules.

## 🚀 Features

- Log database operations (create, write, unlink, search, search_read)
- Configure logging per model
- Store log entries in the database for later analysis
- Automatic cleanup of old log entries
- User-friendly interface for managing logging configurations
- Real-time logging to Odoo server logs
- Thread-safe implementation with recursion prevention

## 🔧 Installation

1. Clone this repository into your Odoo addons directory:

2. Update your Odoo configuration file to include the path to the module:
```conf
addons_path = /path/to/odoo/addons,/path/to/odoo/custom/addons
```

3. Restart your Odoo server
4. Go to Apps and install "Debug Logger"

## 🎯 Usage

### Basic Configuration

1. Go to Debug Tools → Logger Settings
2. Create a new configuration or use the default one
3. Configure which operations to log:
   - Create operations
   - Write operations
   - Delete operations
   - Search operations
   - Search Read operations
4. Select specific models to log or leave empty to log all models
5. Enable/disable storing of log entries
6. Set maximum number of entries to keep if storage is enabled

### Viewing Logs

#### Server Logs
Logs are written to the standard Odoo log file with the INFO level:
```
[CREATE] on res.partner
vals_list: [{'name': 'Test Partner', 'email': 'test@example.com'}]
```

#### Stored Logs
If storage is enabled:
1. Go to Debug Tools → Log Entries
2. Use filters and group by options to analyze the logs
3. Click on individual entries to see detailed information


## 🔒 Security

The module is accessible only to users in the System Administration group (base.group_system) to ensure sensitive debugging information remains protected.