"""Help command for listing available commands."""

from __future__ import annotations

from ..cli import _discover_commands, _get_current_package_name, _get_package_name  # noqa: TID252
from ..commands import register_command  # noqa: TID252


def _help_command(_args: list[str]) -> bool:
    """Display available commands."""
    package_name = _get_package_name()
    current_package = _get_current_package_name()

    if package_name != current_package:
        commands = _discover_commands(primary_package=package_name, additional_packages=[current_package])
    else:
        commands = _discover_commands()

    print(f"Usage: {package_name} <command> [args...]")
    print("\nCommands:")
    for cmd_name, cmd_info in sorted(commands.items()):
        description = cmd_info.get("description", "")
        print(f"  {cmd_name:<12} {description}")
    print("\nExamples:")
    for cmd_name in list(commands.keys())[:3]:
        print(f"  {package_name} {cmd_name}")
    return True


register_command("help", _help_command, "Display available commands")

