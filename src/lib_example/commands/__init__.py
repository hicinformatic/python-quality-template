"""Command registry with automatic discovery."""

from __future__ import annotations

from typing import TYPE_CHECKING, TypedDict

if TYPE_CHECKING:
    from collections.abc import Callable


class CommandInfo(TypedDict):
    """Command information structure."""
    func: Callable[[list[str]], bool]
    description: str


# Registry for all commands - explicitly typed
REGISTERED_COMMANDS: dict[str, CommandInfo] = {}


def register_command(
    name: str,
    func: Callable[[list[str]], bool],
    description: str = "",
) -> None:
    """Register a command function.

    Args:
        name: Command name
        func: Command function that takes args list and returns bool
        description: Command description for help

    Raises:
        ValueError: If command name is already registered
    """
    if name in REGISTERED_COMMANDS:
        raise ValueError(f"Command '{name}' is already registered")

    REGISTERED_COMMANDS[name] = CommandInfo(
        func=func,
        description=description or func.__doc__ or "",
    )


# Auto-discover commands from this package
def _auto_discover_commands() -> None:
    """Automatically discover and register commands from command modules."""
    package = __package__
    if not package:
        return

    # Get the package path
    from pathlib import Path
    package_path = Path(__file__).parent

    # Import all modules in this package
    import importlib
    import pkgutil

    for _, modname, ispkg in pkgutil.iter_modules([str(package_path)]):
        if not ispkg and modname != "__init__":
            from contextlib import suppress
            with suppress(Exception):
                importlib.import_module(f"{package}.{modname}")
                # Commands should register themselves on import


# Auto-discover on import
_auto_discover_commands()


def get_registered_commands() -> dict[str, CommandInfo]:
    """Get all registered commands.

    Returns:
        Dictionary of command names to CommandInfo.
    """
    # Ensure commands are loaded
    _auto_discover_commands()
    return REGISTERED_COMMANDS.copy()

