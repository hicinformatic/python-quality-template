"""Command-line interface with automatic command discovery."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from .commands import CommandInfo


def _get_current_package_name() -> str:
    """Get the current package name (providerkit) dynamically.

    Returns:
        Current package name (e.g., 'providerkit').
    """
    if __package__:
        return __package__.split(".")[0]
    if __name__ and "." in __name__:
        return __name__.split(".")[0]
    return "providerkit"


def _detect_package_from_frames() -> str | None:
    """Detect package name from call stack frames.

    Returns:
        Package name if found, None otherwise.
    """
    from contextlib import suppress

    current_package = _get_current_package_name()
    with suppress(Exception):
        import inspect
        frame = inspect.currentframe()
        for _ in range(10):
            if not frame:
                break
            frame = frame.f_back
            if frame:
                caller_package = frame.f_globals.get("__package__")
                if caller_package and not caller_package.startswith(current_package):
                    result: str = caller_package.split(".")[0]
                    return result
    return None


def _get_package_name_from_context() -> str:
    """Get package name from current module context.

    Returns:
        Package name if found, 'mypackage' otherwise.
    """
    if __package__:
        return __package__.split(".")[0]
    if __name__ and "." in __name__:
        return __name__.split(".")[0]
    try:
        from pathlib import Path
        if __file__:
            parent_dir = Path(__file__).parent.name
            if parent_dir and parent_dir != "cli.py":
                return parent_dir
    except Exception:
        pass
    return "mypackage"


def _get_package_name(package: str | None = None) -> str:
    """Get the package name dynamically.

    Args:
        package: Optional package name. If None, tries to detect from caller's context.

    Returns:
        Package name (e.g., 'mypackage')
    """
    if package:
        return package.split(".")[0]

    detected = _detect_package_from_frames()
    if detected:
        return detected

    return _get_package_name_from_context()


def _discover_commands_from_package(package_name: str) -> dict[str, CommandInfo]:
    """Discover commands from a specific package.

    Args:
        package_name: Name of the package to discover commands from.

    Returns:
        Dictionary mapping command names to their functions and descriptions.
    """
    result: dict[str, CommandInfo] = {}

    try:
        import importlib
        import pkgutil
        from contextlib import suppress
        from pathlib import Path

        commands_module = importlib.import_module(f"{package_name}.commands")

        if hasattr(commands_module, "get_registered_commands"):
            for name, info in commands_module.get_registered_commands().items():
                result[name] = {"func": info["func"], "description": info["description"]}
        elif hasattr(commands_module, "REGISTERED_COMMANDS"):
            package_path = Path(commands_module.__file__).parent if commands_module.__file__ else Path()
            allowed_modules = {f.stem for f in package_path.glob("*.py") if f.stem != "__init__"} if package_path.exists() else set()

            for _, modname, ispkg in pkgutil.iter_modules([str(package_path)]):
                if not ispkg and modname in allowed_modules:
                    with suppress(Exception):
                        importlib.import_module(f"{package_name}.commands.{modname}")

            if hasattr(commands_module, "_auto_discover_commands"):
                commands_module._auto_discover_commands()

            for name, info in commands_module.REGISTERED_COMMANDS.items():
                result[name] = {"func": info["func"], "description": info["description"]}
    except ImportError:
        pass

    return result


def _discover_current_package_commands() -> dict[str, CommandInfo]:
    """Discover commands from the current package (providerkit).

    Returns:
        Dictionary mapping command names to their functions and descriptions.
    """
    result: dict[str, CommandInfo] = {}
    try:
        import importlib
        import pkgutil
        from contextlib import suppress
        from pathlib import Path

        from . import commands

        package = commands.__package__
        if package:
            package_path = Path(commands.__file__).parent if commands.__file__ else Path()
            allowed_modules = {f.stem for f in package_path.glob("*.py") if f.stem != "__init__"} if package_path.exists() else set()

            for _, modname, ispkg in pkgutil.iter_modules([str(package_path)]):
                if not ispkg and modname in allowed_modules:
                    with suppress(Exception):
                        importlib.import_module(f"{package}.{modname}")

            for name, info in commands.REGISTERED_COMMANDS.items():
                result[name] = info
    except ImportError:
        pass
    return result


def _merge_additional_commands(
    result: dict[str, CommandInfo],
    additional_packages: list[str],
) -> None:
    """Merge commands from additional packages into result.

    Args:
        result: Dictionary to merge commands into.
        additional_packages: List of package names to discover commands from.
    """
    for package_name in additional_packages:
        additional_commands = _discover_commands_from_package(package_name)
        for name, info in additional_commands.items():
            if name not in result:
                result[name] = info


def _discover_commands(
    primary_package: str | None = None,
    additional_packages: list[str] | None = None,
) -> dict[str, CommandInfo]:
    """Discover commands from primary package and optionally additional packages.

    Args:
        primary_package: Primary package name. If None, uses current package (providerkit).
        additional_packages: List of package names to discover commands from.
            Commands from primary package take priority.

    Returns:
        Dictionary mapping command names to their functions and descriptions.
    """
    result: dict[str, CommandInfo] = {}

    if primary_package is None:
        result = _discover_current_package_commands()
    else:
        primary_commands = _discover_commands_from_package(primary_package)
        result.update(primary_commands)

    if additional_packages:
        _merge_additional_commands(result, additional_packages)

    return result


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point."""
    args = list(argv if argv is not None else sys.argv[1:])
    commands = _discover_commands()

    if not args:
        package_name = _get_package_name()
        print(f"Usage: {package_name} <command> [args...]")
        print("\nCommands:")
        for cmd_name, cmd_info in sorted(commands.items()):
            description = cmd_info["description"]
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
