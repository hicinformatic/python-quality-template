"""Linting checks module."""

from __future__ import annotations

import platform

from services import utils
from services.quality import common

# Import from common
PROJECT_ROOT = common.PROJECT_ROOT
VENV_BIN = common.VENV_BIN
print_info = common.print_info
print_success = common.print_success
print_error = common.print_error
print_warning = common.print_warning
print_header = common.print_header
print_separator = common.print_separator
venv_exists = common.venv_exists
get_code_directories = common.get_code_directories
run_command = common.run_command

# Import additional utils not in common
print_results = utils.print_results
summarize_results = utils.summarize_results
print_summary = utils.print_summary


def task_lint() -> bool:
    """Run linting checks."""
    if not common.check_venv_required():
        return False

    print_separator()
    print_header("LINTING CHECKS")
    print_separator()

    ruff = VENV_BIN / ("ruff.exe" if platform.system() == "Windows" else "ruff")
    mypy = VENV_BIN / ("mypy.exe" if platform.system() == "Windows" else "mypy")
    semgrep = VENV_BIN / ("semgrep.exe" if platform.system() == "Windows" else "semgrep")
    pylint = VENV_BIN / ("pylint.exe" if platform.system() == "Windows" else "pylint")
    targets = get_code_directories()

    results = {}

    # Ruff check
    print("\n" + "-" * 70)
    print_info("1/4 - Running Ruff")
    print("-" * 70)
    success, _ = run_command([str(ruff), "check", *targets], check=False, capture_output=True)
    if success:
        print_success("✓ Ruff: No issues found")
        results["ruff"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ Ruff: Issues found")
        results["ruff"] = {"status": False, "errors": 1, "warnings": 0}

    # MyPy type checking
    print("\n" + "-" * 70)
    print_info("2/4 - Running MyPy")
    print("-" * 70)
    success, _ = run_command([str(mypy), *targets], check=False, capture_output=True)
    if success:
        print_success("✓ MyPy: No type issues found")
        results["mypy"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ MyPy: Type issues found")
        results["mypy"] = {"status": False, "errors": 1, "warnings": 0}

    # Pylint - Code quality and duplicate code detection
    print("\n" + "-" * 70)
    print_info("3/4 - Running Pylint (Code Quality & Duplicate Code)")
    print("-" * 70)
    success, _ = run_command(
        [str(pylint), "--disable=all", "--enable=duplicate-code", *targets],
        check=False,
        capture_output=True,
    )
    if success:
        print_success("✓ Pylint: No duplicate code or quality issues found")
        results["pylint"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ Pylint: Duplicate code or quality issues found")
        results["pylint"] = {"status": False, "errors": 1, "warnings": 0}

    # Semgrep - Code quality and security patterns
    print("\n" + "-" * 70)
    print_info("4/4 - Running Semgrep (Code Quality & Security Patterns)")
    print("-" * 70)
    semgrep_cmd = utils.build_semgrep_command(semgrep, targets)
    success, _ = run_command(semgrep_cmd, check=False, capture_output=True)
    if success:
        print_success("✓ Semgrep: No issues found")
        results["semgrep"] = {"status": True, "errors": 0, "warnings": 0}
    else:
        print_warning("⚠ Semgrep: Issues found")
        results["semgrep"] = {"status": False, "errors": 1, "warnings": 0}

    # Print results summary
    print_results(results, title="Linting Results", format="table")  # type: ignore[arg-type]
    summary = summarize_results(results)  # type: ignore[arg-type]
    print_summary(summary)

    return all(r.get("status", False) for r in results.values())

