"""Version command."""

from __future__ import annotations

# ruff: noqa: TID252  # Relative imports needed for dynamic package name
from ..commands import register_command


def _get_package_name() -> str:
    """Get the package name dynamically.

    Returns:
        Package name (e.g., 'mypackage')
    """
    # Get package name from current module's package
    package = __package__
    if package:
        # Extract root package name (first part before any dots)
        # For 'mypackage.commands.version', this gives 'mypackage'
        return package.split(".")[0]
    # Fallback: use module name if package is not available
    if __name__ and "." in __name__:
        return __name__.split(".")[0]
    return "mypackage"  # Final fallback


def _version_command(_args: list[str]) -> bool:
    """Show version information.

    Args:
        _args: Command arguments (unused for this command)

    Returns:
        True on success
    """
    # ruff: noqa: TID252  # Relative imports needed for dynamic package name
    from .. import __version__

    package_name = _get_package_name()
    print(f"{package_name} version {__version__}")
    return True


# Auto-register on import - explicit and type-safe
register_command("version", _version_command, "Show version information")

