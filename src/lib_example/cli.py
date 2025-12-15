"""Command-line interface with automatic command discovery."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence


def _get_package_name() -> str:
    """Get the package name dynamically.

    Returns:
        Package name (e.g., 'mypackage')
    """
    # Get package name from current module's package
    # When cli.py is in a package, __package__ is the package name
    # e.g., 'mypackage' or any other package name
    package = __package__
    if package:
        # Extract root package name (first part before any dots)
        # For 'mypackage.cli', this gives 'mypackage'
        return package.split(".")[0]
    # Fallback: use module name if package is not available
    # For '__main__' or direct execution, try to extract from __name__
    if __name__ and "." in __name__:
        return __name__.split(".")[0]
    # Last fallback: try to get from __file__ path
    try:
        from pathlib import Path
        if __file__:
            # Get parent directory name (should be the package name)
            parent_dir = Path(__file__).parent.name
            if parent_dir and parent_dir != "cli.py":
                return parent_dir
    except Exception:
        pass
    return "mypackage"  # Final fallback


def _discover_commands() -> dict[str, dict[str, Callable[[list[str]], bool] | str]]:
    """Discover commands from commands module.

    Returns:
        Dictionary mapping command names to their functions and descriptions.
    """
    try:
        # Force import of all command modules to trigger registration
        import importlib
        import pkgutil
        from contextlib import suppress
        from pathlib import Path

        from . import commands

        package = commands.__package__
        if not package:
            return {}

        package_path = Path(commands.__file__).parent if commands.__file__ else Path()

        # Import all command modules
        # Security: Build whitelist from actual .py files in commands directory
        # to prevent arbitrary code execution via importlib.import_module()
        allowed_modules: set[str] = set()
        if package_path.exists():
            for py_file in package_path.glob("*.py"):
                if py_file.stem != "__init__":
                    allowed_modules.add(py_file.stem)

        for _, modname, ispkg in pkgutil.iter_modules([str(package_path)]):
            if not ispkg and modname in allowed_modules:
                with suppress(Exception):
                    importlib.import_module(f"{package}.{modname}")

        # Convert CommandInfo to expected format
        result: dict[str, dict[str, Callable[[list[str]], bool] | str]] = {}
        for name, info in commands.REGISTERED_COMMANDS.items():
            result[name] = {
                "func": info["func"],
                "description": info["description"],
            }
        return result
    except ImportError:
        return {}


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point."""
    args = list(argv if argv is not None else sys.argv[1:])
    commands = _discover_commands()

    if not args:
        package_name = _get_package_name()
        print(f"Usage: {package_name} <command> [args...]")
        print("\nCommands:")
        for cmd_name, cmd_info in sorted(commands.items()):
            description = cmd_info.get("description", "")
            print(f"  {cmd_name:<12} {description}")
        print("\nExamples:")
        for cmd_name in list(commands.keys())[:3]:
            print(f"  {package_name} {cmd_name}")
        return 1

    command = args[0].lower()

    if command in commands:
        cmd_info = commands[command]
        cmd_func = cmd_info["func"]
        # Type narrowing: we know func is Callable from CommandInfo structure
        if isinstance(cmd_func, str):
            print(f"Invalid command function for '{command}'", file=sys.stderr)
            return 1
        # Cast to Callable for type checker
        func = cast("Callable[[list[str]], bool]", cmd_func)
        try:
            result = func(args[1:] if len(args) > 1 else [])
            return 0 if result else 1
        except Exception as exc:
            print(f"Error executing command '{command}': {exc}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            return 1
    else:
        print(f"Unknown command: {command}", file=sys.stderr)
        print(f"Available commands: {', '.join(sorted(commands.keys()))}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
