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
print_info = utils.print_info
print_success = utils.print_success

# Import task functions from modules
task_lint = lint.task_lint
task_security = security.task_security
task_test = test.task_test
task_complexity = complexity.task_complexity
task_cleanup = cleanup.task_cleanup


def task_all() -> bool:
    """Run all quality checks in sequence."""
    print_info("Running all quality checks...")
    print_info("This will run: lint, security, test, complexity, cleanup")
    print("")

    results = {
        "lint": False,
        "security": False,
        "test": False,
        "complexity": False,
        "cleanup": False,
    }

    # Run all checks
    results["lint"] = task_lint()
    print("")
    results["security"] = task_security()
    print("")
    results["test"] = task_test()
    print("")
    results["complexity"] = task_complexity()
    print("")
    results["cleanup"] = task_cleanup()

    # Summary
    print("\n" + "=" * 70)
    print_info("QUALITY CHECKS SUMMARY")
    print("=" * 70)
    for check_name, check_result in results.items():
        status = "✓ PASS" if check_result else "✗ FAIL"
        print(f"  {check_name:<12} {status}")

    all_passed = all(results.values())
    print("=" * 70)
    if all_passed:
        print_success("All quality checks passed!")
    else:
        print_error("Some quality checks failed. Please review the output above.")
    print("=" * 70)

    return all_passed


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python quality.py <command>")
        print("\nCommands:")
        print("  all       Run all quality checks (lint, security, test, complexity, cleanup)")
        print("  lint      Run linting checks (ruff, mypy, pylint, semgrep)")
        print("  security  Run security checks (bandit, safety, pip-audit, semgrep)")
        print("  test      Run tests (pytest)")
        print("  complexity  Analyze code complexity (radon)")
        print("  cleanup   Detect unused code, imports, and redundancies (vulture, autoflake, pylint)")
        return 1

    command = sys.argv[1].lower()

    if command == "all":
        success = task_all()
    elif command == "lint":
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
        print("Available commands: all, lint, security, test, complexity, cleanup")
        return 1

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

