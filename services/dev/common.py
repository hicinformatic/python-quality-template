"""Common imports and utilities for dev modules.

This module provides a centralized way to import common utilities
to reduce code duplication across dev modules.
"""

from __future__ import annotations

from services import utils

# Export common constants
PROJECT_ROOT = utils.PROJECT_ROOT
VENV_BIN = utils.VENV_BIN
VENV_DIR = utils.VENV_DIR
PIP = utils.PIP

# Export common utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning
venv_exists = utils.venv_exists
run_command = utils.run_command

