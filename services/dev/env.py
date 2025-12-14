"""Environment management tasks."""

from __future__ import annotations

import platform
import shutil
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Use common imports from dev.common
from services.dev import common

# Import from common
PROJECT_ROOT = common.PROJECT_ROOT
VENV_BIN = common.VENV_BIN
VENV_DIR = common.VENV_DIR
PIP = common.PIP
print_info = common.print_info
print_success = common.print_success
print_error = common.print_error
print_warning = common.print_warning
venv_exists = common.venv_exists
run_command = common.run_command


def install_build_dependencies() -> bool:
    """Install build dependencies."""
    success, _ = run_command([str(PIP), "install", "--upgrade", "pip", "setuptools", "wheel"])
    return success


def task_venv() -> bool:
    """Create a virtual environment."""
    if venv_exists():
        print_warning("Virtual environment already exists.")
        return True

    python_cmd = "python3" if platform.system() != "Windows" else "python"
    print_info("Creating virtual environment...")
    success, _ = run_command([python_cmd, "-m", "venv", str(VENV_DIR)], check=False)
    if not success:
        return False

    print_success(f"Virtual environment created at {VENV_DIR}")
    activation = (
        f"{VENV_DIR}\\Scripts\\activate"
        if platform.system() == "Windows"
        else f"source {VENV_DIR}/bin/activate"
    )
    print_info(f"Activate it with: {activation}")
    return True


def task_venv_clean() -> bool:
    """Recreate the virtual environment."""
    if venv_exists():
        print_info("Removing existing virtual environment...")
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        print_success("Virtual environment removed.")
    return task_venv()


def task_install() -> bool:
    """Install the package in production mode."""
    if not venv_exists() and not task_venv():
        return False

    print_info("Installing package (production)...")
    if not install_build_dependencies():
        return False

    success, _ = run_command([str(PIP), "install", "."], check=False)
    if not success:
        return False

    # Install requirements.txt if it exists
    requirements = PROJECT_ROOT / "requirements.txt"
    if requirements.exists():
        print_info("Installing dependencies from requirements.txt...")
        run_command([str(PIP), "install", "-r", str(requirements)], check=False)

    print_success("Installation complete.")
    return True


def _install_requirements_file(req_path: Path) -> None:
    """Install dependencies from a requirements file if it exists."""
    if req_path.exists():
        print_info(f"Installing dependencies from {req_path.name}...")
        run_command([str(PIP), "install", "-r", str(req_path)], check=False)


def _install_dev_dependencies_from_file() -> bool:
    """Install development dependencies from requirements-quality.txt if it exists."""
    requirements_quality = PROJECT_ROOT / "requirements-quality.txt"
    if not requirements_quality.exists():
        return False

    print_info("Installing development dependencies from requirements-quality.txt...")
    success, _ = run_command([str(PIP), "install", "-r", str(requirements_quality)], check=False)
    return success


def _install_dev_dependencies_fallback() -> None:
    """Install development dependencies using fallback methods."""
    print_info("Installing development dependencies from pyproject.toml...")
    deps = ["lint", "security", "test", "quality"]
    for dep_group in deps:
        success, _ = run_command([str(PIP), "install", "-e", f".[{dep_group}]"], check=False)
        if not success:
            print_warning(f"Failed to install {dep_group} dependencies")

    requirements_files = [
        "requirements-quality.txt",
        "requirements-django.txt",
    ]
    for req_file in requirements_files:
        _install_requirements_file(PROJECT_ROOT / req_file)


def task_install_dev() -> bool:
    """Install the package in editable mode with dev dependencies."""
    if not venv_exists() and not task_venv():
        return False

    print_info("Installing package (development)...")
    if not install_build_dependencies():
        return False

    success, _ = run_command([str(PIP), "install", "-e", "."], check=False)
    if not success:
        return False

    _install_requirements_file(PROJECT_ROOT / "requirements.txt")

    if _install_dev_dependencies_from_file():
        print_success("Development installation complete.")
        return True

    print_warning("Failed to install from requirements-quality.txt, trying fallback methods...")
    _install_dev_dependencies_fallback()

    print_success("Development installation complete.")
    return True

