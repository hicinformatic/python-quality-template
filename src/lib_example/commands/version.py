"""Version command."""

from __future__ import annotations

from ..cli import _get_current_package_name, _get_package_name  # noqa: TID252
from ..commands import register_command  # noqa: TID252


def _version_command(_args: list[str]) -> bool:
    """Show version information."""
    package_name = _get_package_name()
    current_package = _get_current_package_name()

    if package_name != current_package:
        try:
            package_module = __import__(package_name, fromlist=["__version__"])
            version = getattr(package_module, "__version__", "unknown")
            print(f"{package_name} version {version}")
            return True
        except ImportError:
            pass

    current_module = __import__(current_package, fromlist=["__version__"])
    version = getattr(current_module, "__version__", "unknown")
    print(f"{package_name} version {version}")
    return True


register_command("version", _version_command, "Show version information")

