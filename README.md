# Debug Logger for Odoo

A powerful and configurable logging module for Odoo, designed to enhance debugging by logging database operations (`create`, `write`, `unlink`, `search`) with fine-grained control over methods and models. Easily enable or disable logging, select specific models, and choose methods via the Odoo interface under **Settings > Technical**. Ideal for developers and administrators who need better insights into system behavior during development or production.

---

## Features

This repository contains a fully configurable Odoo module that makes it easier to track model changes and debug issues by logging key database operations. The module allows users to:

- **Enable/Disable** logging through a boolean switch.
- **Select specific methods** to log (e.g., `create`, `write`, `unlink`, `search`).
- **Choose specific models** or log all models.

### Configuration

- Access the debub parameters via the **Odoo UI** under **Settings > Technical > System Configuration**.

---

## Benefits

- Gain **better visibility** into Odoo's internal operations.
- Simplify **troubleshooting** during module development or system testing.
