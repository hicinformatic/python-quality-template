"""Code cleanup analysis module."""

from __future__ import annotations

import platform

# Use common imports from quality.common
from services.quality import common

# Import from common
VENV_BIN = common.VENV_BIN
print_info = common.print_info
print_success = common.print_success
print_error = common.print_error
print_warning = common.print_warning
print_separator = common.print_separator
venv_exists = common.venv_exists
get_code_directories = common.get_code_directories
run_command = common.run_command


def task_cleanup() -> bool:
    """Detect unused code, imports, and redundancies."""
    if not common.check_venv_required():
        return False

    print_separator()
    print_info("CODE CLEANUP ANALYSIS")
    print_separator()

    vulture = VENV_BIN / ("vulture.exe" if platform.system() == "Windows" else "vulture")
    autoflake = VENV_BIN / ("autoflake.exe" if platform.system() == "Windows" else "autoflake")
    pylint = VENV_BIN / ("pylint.exe" if platform.system() == "Windows" else "pylint")
    targets = get_code_directories()

    results = {
        "vulture": False,
        "autoflake": False,
        "pylint": False,
    }

    # Vulture - Dead code detection
    print("\n" + "-" * 70)
    print_info("1/3 - Running Vulture (Dead Code Detection)")
    print("-" * 70)
    success, _ = run_command([str(vulture), *targets, "--min-confidence", "80"], check=False)
    if success:
        print_success("✓ Vulture: No dead code found")
        results["vulture"] = True
    else:
        print_warning("⚠ Vulture: Potential dead code detected (review above)")

    # Autoflake - Unused imports check
    print("\n" + "-" * 70)
    print_info("2/3 - Running Autoflake (Unused Imports Check)")
    print("-" * 70)
    autoflake_cmd = [
        str(autoflake),
        "--check",
        "--recursive",
        "--remove-all-unused-imports",
        "--remove-unused-variables",
    ] + targets
    success, _ = run_command(autoflake_cmd, check=False)
    if success:
        print_success("✓ Autoflake: No unused imports or variables")
        results["autoflake"] = True
    else:
        print_warning("⚠ Autoflake: Unused imports/variables found")

    # Pylint - Code quality and redundancies
    print("\n" + "-" * 70)
    print_info("3/3 - Running Pylint (Code Quality & Redundancies)")
    print("-" * 70)
    success, _ = run_command(
        [str(pylint), *targets, "--fail-under=8.0", "--disable=C0111,C0103,R0903"],
        check=False,
    )
    if success:
        print_success("✓ Pylint: Code quality score >= 8.0/10")
        results["pylint"] = True
    else:
        print_warning("⚠ Pylint: Code quality issues found (review above)")

    all_passed = all(results.values())
    if all_passed:
        print("\n" + "=" * 70)
        print_success("All cleanup checks passed!")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print_warning("Some cleanup checks found issues. Please review the output above.")
        print("=" * 70)

    return all_passed

