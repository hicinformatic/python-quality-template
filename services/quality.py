#!/usr/bin/env python3
"""Quality checks script for Python projects.

Provides commands for linting, security checks, and testing.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _load_modules() -> tuple:
    """Load required modules after adding parent to sys.path."""
    _services_dir = Path(__file__).resolve().parent
    _project_root = _services_dir.parent
    if str(_project_root) not in sys.path:
        sys.path.insert(0, str(_project_root))

    from services import utils
    from services.quality import cleanup, complexity, lint, security, test

    return utils, cleanup, complexity, lint, security, test


utils, cleanup, complexity, lint, security, test = _load_modules()

# Import utility functions for error handling
print_error = utils.print_error

# Import task functions from modules
task_lint = lint.task_lint
task_security = security.task_security
task_test = test.task_test
task_complexity = complexity.task_complexity
task_cleanup = cleanup.task_cleanup


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python quality.py <command>")
        print("\nCommands:")
        print("  lint      Run linting checks (ruff, mypy, pylint, semgrep)")
        print("  security  Run security checks (bandit, safety, pip-audit, semgrep)")
        print("  test      Run tests (pytest)")
        print("  complexity  Analyze code complexity (radon)")
        print("  cleanup   Detect unused code, imports, and redundancies (vulture, autoflake, pylint)")
        return 1

    command = sys.argv[1].lower()

    if command == "lint":
        success = task_lint()
    elif command == "security":
        success = task_security()
    elif command == "test":
        success = task_test()
    elif command == "complexity":
        success = task_complexity()
    elif command == "cleanup":
        success = task_cleanup()
    else:
        print_error(f"Unknown command: {command}")
        print("Available commands: lint, security, test, complexity, cleanup")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

