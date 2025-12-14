"""Common imports and utilities for quality modules.

This module provides a centralized way to import common utilities
to reduce code duplication across quality modules.
"""

from __future__ import annotations

from services import utils

# Export common constants
PROJECT_ROOT = utils.PROJECT_ROOT
VENV_BIN = utils.VENV_BIN

# Export common utility functions
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning
print_header = utils.print_header
print_separator = utils.print_separator
venv_exists = utils.venv_exists
get_code_directories = utils.get_code_directories
run_command = utils.run_command
check_venv_required = utils.check_venv_required

