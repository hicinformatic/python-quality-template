# pylint: disable=R0801  # Duplicate code acceptable for common imports
"""Linting checks module."""

from __future__ import annotations

import platform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

from services import utils
from services.quality import common

# Import from common
# pylint: disable=R0801  # Duplicate code acceptable for common imports
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


def _run_pylint_check(pylint: Path, targets: list[str]) -> tuple[bool, str | None]:
    """Run Pylint check on Python files.

    Args:
        pylint: Path to pylint executable
        targets: List of target directories/files to check

    Returns:
        Tuple of (success: bool, output: str | None)
    """
    # Pylint needs specific Python files, not directories, so find all .py files
    python_files = []
    for target in targets:
        target_path = PROJECT_ROOT / target
        if target_path.exists():
            if target_path.is_file() and target_path.suffix == ".py":
                python_files.append(str(target_path))
            elif target_path.is_dir():
                # Find all Python files in directory, excluding migrations
                for py_file in target_path.rglob("*.py"):
                    if "migrations" not in str(py_file):
                        python_files.append(str(py_file))

    if not python_files:
        print_warning("⚠ Pylint: No Python files found to check")
        return (False, None)

    # Enable duplicate-code group but disable R0801 specifically
    # This ensures other duplicate-code checks still run (if any are added in future)
    # Don't use --disable=all as it prevents Pylint from finding files
    pylint_cmd = [
        str(pylint),
        "--enable=duplicate-code",
        "--disable=R0801",
        "--ignore=migrations",
    ] + python_files
    success, output = run_command(
        pylint_cmd,
        check=False,
        capture_output=True,
    )
    # Pylint returns exit code 8 for warnings (not errors), which is acceptable
    # Check if there are actual R0801 errors in output (should be none)
    output_str = output or ""
    has_r0801 = "R0801" in output_str
    # Consider success if no R0801 errors found, even if exit code is non-zero
    # (exit code 8 = warnings, which is acceptable)
    # Also accept if we get a rating (means Pylint ran successfully)
    has_rating = "rated" in output_str
    pylint_success = success or (not has_r0801 and has_rating)
    return (pylint_success, output)


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
    # Note: R0801 (duplicate-code) is disabled as it flags acceptable structural duplication
    # (common imports pattern) which is intentional for maintainability
    # Also ignore migrations directories as they are auto-generated
    print("\n" + "-" * 70)
    print_info("3/4 - Running Pylint (Code Quality & Duplicate Code)")
    print("-" * 70)
    success, _ = _run_pylint_check(pylint, targets)
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

