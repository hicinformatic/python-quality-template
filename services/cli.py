#!/usr/bin/env python3
"""CLI service for running library CLI commands."""

from __future__ import annotations

import sys
from pathlib import Path

# Use the standard loader from utils (handles sys.path setup)
from services import utils as utils_module

utils = utils_module.load_service_utils()
print_error = utils.print_error
print_info = utils.print_info


def main() -> int:
    """Main entry point."""
    project_root = Path(__file__).resolve().parent.parent
    src_path = project_root / "src"

    if src_path.exists():
        sys.path.insert(0, str(src_path))

    try:
        from lib_example.cli import main as cli_main

        args = sys.argv[1:] if len(sys.argv) > 1 else []
        exit_code = cli_main(args)
        return int(exit_code)
    except ImportError as exc:
        print_error(f"Failed to import library CLI: {exc}")
        print_info("Make sure the library is installed in development mode.")
        return 1
    except Exception as exc:
        print_error(f"Error running CLI: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())

