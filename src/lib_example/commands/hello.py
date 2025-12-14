"""Hello command."""

from __future__ import annotations

from lib_example.commands import register_command


def _hello_command(_args: list[str]) -> bool:
    """Display a friendly greeting.

    Args:
        _args: Command arguments (unused for this command)

    Returns:
        True on success
    """
    from lib_example import hello_world

    print(hello_world())
    return True


# Auto-register on import - explicit and type-safe
register_command("hello", _hello_command, "Display a friendly greeting")

