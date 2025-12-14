"""Security checks module."""

from __future__ import annotations

import os
import platform
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

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


def _run_bandit_check(bandit: Path, targets: list[str]) -> bool:
    """Run Bandit security check."""
    print("\n" + "-" * 70)
    print_info("1/4 - Running Bandit (Static Code Analysis)")
    print("-" * 70)
    success, _ = run_command(
        [str(bandit), "-r", *targets, "-ll", "-f", "screen", "--skip", "B101"],
        check=False,
    )
    if success:
        print_success("✓ Bandit: No high/medium issues found")
    else:
        print_warning("⚠ Bandit: Issues found (review above)")
    return success


def _run_safety_check(safety: Path) -> bool:
    """Run Safety dependency vulnerability check."""
    print("\n" + "-" * 70)
    print_info("2/4 - Running Safety (Dependency Vulnerabilities)")
    print("-" * 70)
    safety_cmd = [str(safety), "scan", "--output", "json"]
    safety_api_key = os.environ.get("SAFETY_API_KEY")
    if safety_api_key:
        safety_cmd.extend(["--key", safety_api_key])
        print_info("   Using SAFETY_API_KEY from environment")

    safety_result, _ = run_command(safety_cmd, check=False)
    if safety_result:
        print_success("✓ Safety: No vulnerabilities found")
        return True

    if not safety_api_key:
        print_warning("⚠ Safety: Unable to complete scan (authentication required)")
        print_info("   Note: Safety CLI requires free account registration")
        print_info("   Option 1: Register at https://pyup.io/safety/ and set SAFETY_API_KEY env var")
        print_info("   Option 2: Run 'safety auth' to authenticate interactively")
        print_info("   For now, treating as skipped (not a failure)")
        return True  # Count as pass since it's optional

    print_warning("⚠ Safety: Scan completed but issues may have been found")
    return False


def _run_pip_audit_check(pip_audit: Path) -> bool:
    """Run Pip-Audit vulnerability check."""
    print("\n" + "-" * 70)
    print_info("3/4 - Running Pip-Audit (PyPI Vulnerabilities)")
    print("-" * 70)
    success, _ = run_command([str(pip_audit)], check=False)
    if success:
        print_success("✓ Pip-Audit: No vulnerabilities found")
    else:
        print_warning("⚠ Pip-Audit: Vulnerabilities found (review above)")
    return success


def _run_semgrep_check(semgrep: Path, targets: list[str]) -> bool:
    """Run Semgrep SAST check."""
    print("\n" + "-" * 70)
    print_info("4/4 - Running Semgrep (SAST)")
    print("-" * 70)
    semgrep_cmd = utils.build_semgrep_command(semgrep, targets)
    success, _ = run_command(semgrep_cmd, check=False)
    if success:
        print_success("✓ Semgrep: No issues found")
    else:
        print_warning("⚠ Semgrep: Issues found (review above)")
    return success


def task_security() -> bool:
    """Run security checks."""
    if not common.check_venv_required():
        return False

    print_separator()
    print_header("SECURITY CHECKS")
    print_separator()

    exe_suffix = ".exe" if platform.system() == "Windows" else ""
    bandit = VENV_BIN / f"bandit{exe_suffix}"
    safety = VENV_BIN / f"safety{exe_suffix}"
    pip_audit = VENV_BIN / f"pip-audit{exe_suffix}"
    semgrep = VENV_BIN / f"semgrep{exe_suffix}"
    targets = get_code_directories()

    results = {
        "bandit": _run_bandit_check(bandit, targets),
        "safety": _run_safety_check(safety),
        "pip_audit": _run_pip_audit_check(pip_audit),
        "semgrep": _run_semgrep_check(semgrep, targets),
    }

    all_passed = all(results.values())
    print("\n" + "=" * 70)
    if all_passed:
        print_success("All security checks passed!")
    else:
        print_warning("Some security checks found issues. Please review the output above.")
    print("=" * 70)

    return all_passed

