"""Command-line interface for lib_example."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Sequence


def main(argv: Sequence[str] | None = None) -> int:
    """Main CLI entry point."""
    args = list(argv if argv is not None else sys.argv[1:])

    if not args:
        print("Usage: lib_example <command> [args...]")
        print("\nCommands:")
        print("  hello    Display a friendly greeting")
        print("  version  Show version information")
        print("\nExamples:")
        print("  lib_example hello")
        print("  lib_example version")
        return 1

    command = args[0].lower()

    if command == "hello":
        from . import hello_world

        print(hello_world())
        return 0
    elif command == "version":
        from . import __version__

        print(f"lib_example version {__version__}")
        return 0
    else:
        print(f"Unknown command: {command}")
        print("Available commands: hello, version")
        return 1


if __name__ == "__main__":
    sys.exit(main())

