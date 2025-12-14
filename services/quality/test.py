"""Test execution module."""

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
run_command = common.run_command


def task_test() -> bool:
    """Run tests."""
    if not common.check_venv_required():
        return False

    print_separator()
    print_info("RUNNING TESTS")
    print_separator()

    pytest = VENV_BIN / ("pytest.exe" if platform.system() == "Windows" else "pytest")

    success, _ = run_command([str(pytest)], check=False)
    if success:
        print("\n" + "=" * 70)
        print_success("All tests passed!")
        print("=" * 70)
        return True
    else:
        print("\n" + "=" * 70)
        print_error("Tests failed. Please review the output above.")
        print("=" * 70)
        return False

