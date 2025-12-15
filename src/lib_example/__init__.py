"""lib example - Example Python library with src/ structure."""

__version__ = "0.1.0"

from .cli import _discover_commands, _get_package_name
from .commands import get_registered_commands, register_command
from .helpers import hello_world

__all__ = [
    "hello_world",
    "register_command",
    "get_registered_commands",
    "_discover_commands",
    "_get_package_name",
]
