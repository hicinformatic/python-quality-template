"""Version command."""

from __future__ import annotations

from lib_example.commands import register_command


def _version_command(_args: list[str]) -> bool:
    """Show version information.

    Args:
        _args: Command arguments (unused for this command)

    Returns:
        True on success
    """
    from lib_example import __version__

    print(f"lib_example version {__version__}")
    return True


# Auto-register on import - explicit and type-safe
register_command("version", _version_command, "Show version information")

