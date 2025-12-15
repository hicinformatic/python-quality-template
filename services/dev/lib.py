# pylint: disable=R0801  # Duplicate code acceptable for common imports
"""Library update tasks."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from services import utils
from services.dev import common

# Import from common
# pylint: disable=R0801  # Duplicate code acceptable for common imports
PROJECT_ROOT = common.PROJECT_ROOT
PIP = common.PIP
print_info = common.print_info
print_success = common.print_success
print_error = common.print_error
print_warning = common.print_warning
venv_exists = common.venv_exists
run_command = common.run_command

# Import additional utils not in common
print_separator = utils.print_separator


def task_update_lib() -> bool:
    """Install or update a library from local directory in editable mode.

    Usage:
      python dev.py update-lib <path_to_library>
      ./service.py dev update-lib path/to/lib

    The library will be installed in editable mode (-e) so changes are
    immediately available without reinstalling.

    Args:
        Path to the library directory (must contain setup.py or pyproject.toml)
    """
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    # Get path from command line arguments
    args = sys.argv[2:] if len(sys.argv) > 2 else []

    if not args:
        print_error("No library path provided.")
        print_info("Usage: python dev.py update-lib <path_to_library>")
        print_info("       ./service.py dev update-lib path/to/lib")
        return False

    target_dir = Path(args[0]).resolve()

    # Handle relative paths
    if not target_dir.is_absolute():
        target_dir = (PROJECT_ROOT / args[0]).resolve()

    if not target_dir.exists():
        print_error(f"Library directory not found at {target_dir}")
        print_info("Provide a valid path: python dev.py update-lib /path/to/library")
        return False

    if not target_dir.is_dir():
        print_error(f"Path is not a directory: {target_dir}")
        return False

    # Check if it looks like a Python package
    has_setup = (target_dir / "setup.py").exists()
    has_pyproject = (target_dir / "pyproject.toml").exists()

    if not (has_setup or has_pyproject):
        print_warning(
            f"Warning: No setup.py or pyproject.toml found in {target_dir}. "
            "This might not be a Python package."
        )

    lib_name = target_dir.name
    print_info(f"Installing {lib_name} into the virtual environment...")
    print_info(f"Library path: {target_dir}")

    success, _ = run_command([str(PIP), "install", "-e", str(target_dir)], check=False)
    if success:
        print_success(f"{lib_name} installed/updated successfully.")
        return True

    print_error(f"Failed to install/update {lib_name}.")
    return False


def _load_libraries_config(config_file: Path) -> list[dict] | None:
    """Load and validate libraries configuration from JSON file."""
    if not config_file.exists():
        print_error(f"Configuration file not found: {config_file}")
        print_info("Create additionallib.json in the project root.")
        print_info("You can copy additionallib.json.example as a template.")
        return None

    print_separator()
    print_info(f"Reading libraries from {config_file.name}")
    print_separator()

    try:
        with open(config_file, encoding="utf-8") as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print_error(f"Invalid JSON in {config_file}: {e}")
        return None
    except Exception as e:
        print_error(f"Error reading {config_file}: {e}")
        return None

    if "libraries" not in config:
        print_error(f"Missing 'libraries' key in {config_file}")
        return None

    libraries = config["libraries"]
    if not isinstance(libraries, list):
        print_error(f"'libraries' must be a list in {config_file}")
        return None

    return libraries


def _validate_library_config(lib_config: dict, idx: int) -> tuple[str, str, str] | None:
    """Validate and extract library configuration."""
    if not isinstance(lib_config, dict):
        print_warning(f"Library entry {idx} is not a dictionary, skipping")
        return None

    lib_name = lib_config.get("name", f"library-{idx}")
    lib_path = lib_config.get("path")
    lib_description = lib_config.get("description", "")

    if not lib_path:
        print_error(f"Library '{lib_name}' missing 'path' field, skipping")
        return None

    return lib_name, lib_path, lib_description


def _resolve_library_path(lib_path: str) -> Path | None:
    """Resolve library path and validate it exists."""
    target_dir = Path(lib_path)
    if not target_dir.is_absolute():
        target_dir = (PROJECT_ROOT / lib_path).resolve()

    if not target_dir.exists():
        print_warning(f"  ⚠ Library directory not found at {target_dir}, skipping")
        return None

    if not target_dir.is_dir():
        print_warning(f"  ⚠ Path is not a directory: {target_dir}, skipping")
        return None

    return target_dir


def _install_library(lib_name: str, target_dir: Path) -> bool:
    """Install a single library in editable mode."""
    print_info(f"  Installing {lib_name}...")
    success, _ = run_command([str(PIP), "install", "-e", str(target_dir)], check=False)

    if success:
        print_success(f"  ✓ {lib_name} installed/updated successfully")
    else:
        print_error(f"  ✗ Failed to install/update {lib_name}")

    print()
    return success


def _process_library(lib_config: dict, idx: int, total: int) -> tuple[str, bool]:
    """Process a single library installation."""
    validated = _validate_library_config(lib_config, idx)
    if validated is None:
        return f"library-{idx}", False

    lib_name, lib_path, lib_description = validated

    print_info(f"[{idx}/{total}] Processing {lib_name}")
    if lib_description:
        print_info(f"  Description: {lib_description}")
    print_info(f"  Path: {lib_path}")

    target_dir = _resolve_library_path(lib_path)
    if target_dir is None:
        return lib_name, False

    success = _install_library(lib_name, target_dir)
    return lib_name, success


def _print_installation_summary(results: dict[str, bool]) -> None:
    """Print installation summary."""
    print_separator()
    print_info("Installation Summary")
    print_separator()

    total = len(results)
    successful = sum(1 for success in results.values() if success)
    failed = total - successful

    for lib_name, success in results.items():
        status = f"{utils.GREEN}✓{utils.NC}" if success else f"{utils.RED}✗{utils.NC}"
        print(f"  {status} {lib_name}")

    print_separator()
    print_info(f"Total: {total} | Successful: {successful} | Failed: {failed}")
    print_separator()


def task_update_additional_libs() -> bool:
    """Install or update libraries listed in additionallib.json.

    Usage:
      python dev.py update-additional-libs
      ./service.py dev update-additional-libs

    Reads the additionallib.json file in the project root and installs
    all libraries listed there in editable mode.

    The JSON file should have the following structure:
    {
      "libraries": [
        {
          "name": "library-name",
          "path": "../path/to/library",
          "description": "Optional description"
        }
      ]
    }
    """
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    config_file = PROJECT_ROOT / "additionallib.json"
    libraries = _load_libraries_config(config_file)
    if libraries is None:
        return False

    if not libraries:
        print_warning("No libraries found in additionallib.json")
        return True

    print_info(f"Found {len(libraries)} library(ies) to install/update\n")

    results = {}
    for idx, lib_config in enumerate(libraries, 1):
        lib_name, success = _process_library(lib_config, idx, len(libraries))
        results[lib_name] = success

    _print_installation_summary(results)
    failed = len(results) - sum(1 for success in results.values() if success)
    return failed == 0

