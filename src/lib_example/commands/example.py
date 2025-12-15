"""Example command with argument handling."""

from __future__ import annotations

from lib_example.commands import register_command


def _example_command(args: list[str]) -> bool:
    """Example command that demonstrates argument handling.

    This command shows how to handle command-line arguments.

    Args:
        args: Command arguments

    Returns:
        True on success, False on failure

    Usage:
        mypackage example
        mypackage example --name "John"
        mypackage example --name "John" --verbose
    """
    name = "World"
    verbose = False

    # Simple argument parsing
    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--name" and i + 1 < len(args):
            name = args[i + 1]
            i += 2
        elif arg == "--verbose" or arg == "-v":
            verbose = True
            i += 1
        elif arg == "--help" or arg == "-h":
            print("Usage: mypackage example [--name NAME] [--verbose]")
            return True
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: mypackage example [--name NAME] [--verbose]")
            return False

    if verbose:
        print(f"Hello, {name}! (verbose mode)")
    else:
        print(f"Hello, {name}!")

    return True


# Auto-register on import - explicit and type-safe
register_command(
    "example",
    _example_command,
    "Example command with argument handling (use --help for details)",
)

