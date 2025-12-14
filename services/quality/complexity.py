"""Code complexity analysis module."""

from __future__ import annotations

import platform

# Use common imports from quality.common
from services.quality import common

# Import from common
VENV_BIN = common.VENV_BIN
print_info = common.print_info
print_success = common.print_success
print_error = common.print_error
print_separator = common.print_separator
venv_exists = common.venv_exists
get_code_directories = common.get_code_directories
run_command = common.run_command


def task_complexity() -> bool:
    """Analyze code complexity with radon."""
    if not common.check_venv_required():
        return False

    print_separator()
    print_info("CODE COMPLEXITY ANALYSIS")
    print_separator()

    radon = VENV_BIN / ("radon.exe" if platform.system() == "Windows" else "radon")
    targets = get_code_directories()

    # Cyclomatic Complexity
    print("\n" + "-" * 70)
    print_info("1/3 - Cyclomatic Complexity (CC)")
    print("-" * 70)
    print_info("A = simple (1-5), B = moderate (6-10), C = complex (11-20)")
    print_info("D = very complex (21-50), E/F = extremely complex (>50)")
    print("")
    run_command([str(radon), "cc", *targets, "-s", "-a"], check=False)

    # Maintainability Index
    print("\n" + "-" * 70)
    print_info("2/3 - Maintainability Index (MI)")
    print("-" * 70)
    print_info("A = highly maintainable, B = good, C = moderate, D/F = hard to maintain")
    print("")
    run_command([str(radon), "mi", *targets, "-s"], check=False)

    # Raw metrics
    print("\n" + "-" * 70)
    print_info("3/3 - Raw Metrics (LOC, LLOC, Comments)")
    print("-" * 70)
    run_command([str(radon), "raw", *targets, "-s"], check=False)

    print("\n" + "=" * 70)
    print_success("Complexity analysis complete!")
    print_info("Tip: Focus on reducing functions with CC > 10 (C or higher)")
    print("=" * 70)

    return True

