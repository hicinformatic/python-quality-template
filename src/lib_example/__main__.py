"""Entry point for running lib_example as a module."""

from __future__ import annotations

from .cli import main

if __name__ == "__main__":
    import sys

    sys.exit(main())

