#!/usr/bin/env python3
"""Template synchronization service.

Synchronizes template files from python-quality-template to target projects.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Use the standard loader from utils (handles sys.path setup)
from services import utils as utils_module

utils = utils_module.load_service_utils()
print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning


def sync_services(template_path: Path, target_path: Path) -> bool:
    """Sync services/* files from template to target project."""
    template_services = template_path / "services"
    target_services = target_path / "services"

    if not template_services.exists():
        print_error(f"Template services directory not found: {template_services}")
        return False

    if not target_services.exists():
        target_services.mkdir(parents=True, exist_ok=True)
        print_info(f"Created services directory: {target_services}")

    files_copied = 0
    dirs_copied = 0

    for item in template_services.iterdir():
        if item.name == "template.py":
            continue

        target_item = target_services / item.name

        if item.is_file():
            if item.suffix == ".py" or item.name in ["__init__.py"]:
                shutil.copy2(item, target_item)
                files_copied += 1
                print_info(f"Copied: {item.name}")
        elif item.is_dir():
            if target_item.exists():
                shutil.rmtree(target_item)
            shutil.copytree(item, target_item, dirs_exist_ok=True)
            dirs_copied += 1
            print_info(f"Copied directory: {item.name}/")

    print_success(f"Synced services: {files_copied} files, {dirs_copied} directories")
    return True


def sync_service_py(template_path: Path, target_path: Path) -> bool:
    """Sync service.py from template to target project."""
    template_service = template_path / "service.py"
    target_service = target_path / "service.py"

    if not template_service.exists():
        print_error(f"Template service.py not found: {template_service}")
        return False

    shutil.copy2(template_service, target_service)
    print_success("Synced service.py")
    return True


def _find_package_dir(base_path: Path) -> Path | None:
    """Find the package directory in src/.

    Args:
        base_path: Base path (project root)

    Returns:
        Path to package directory in src/, or None if not found
    """
    src_path = base_path / "src"
    if not src_path.exists():
        return None

    # Find first directory in src/ that contains __init__.py
    for item in src_path.iterdir():
        if item.is_dir() and not item.name.startswith("_"):
            init_file = item / "__init__.py"
            if init_file.exists():
                return item

    return None


def sync_cli(template_path: Path, target_path: Path) -> bool:
    """Sync CLI files (cli.py, __main__.py, commands/) from template to target project.

    Args:
        template_path: Path to template project
        target_path: Path to target project

    Returns:
        True if synchronization succeeded, False otherwise
    """
    template_package = _find_package_dir(template_path)
    target_package = _find_package_dir(target_path)

    if not template_package:
        print_warning("Template package directory not found in src/. Skipping CLI sync.")
        return True  # Not an error, just skip

    if not target_package:
        print_warning("Target package directory not found in src/. Skipping CLI sync.")
        return True  # Not an error, just skip

    files_copied = 0
    dirs_copied = 0

    # Sync cli.py
    template_cli = template_package / "cli.py"
    target_cli = target_package / "cli.py"
    if template_cli.exists():
        shutil.copy2(template_cli, target_cli)
        files_copied += 1
        print_info(f"Copied: {target_package.name}/cli.py")

    # Sync __main__.py
    template_main = template_package / "__main__.py"
    target_main = target_package / "__main__.py"
    if template_main.exists():
        shutil.copy2(template_main, target_main)
        files_copied += 1
        print_info(f"Copied: {target_package.name}/__main__.py")

    # Sync commands/ directory
    template_commands = template_package / "commands"
    target_commands = target_package / "commands"
    if template_commands.exists() and template_commands.is_dir():
        if target_commands.exists():
            shutil.rmtree(target_commands)
        shutil.copytree(template_commands, target_commands, dirs_exist_ok=True)
        dirs_copied += 1
        print_info(f"Copied directory: {target_package.name}/commands/")

    if files_copied > 0 or dirs_copied > 0:
        print_success(f"Synced CLI: {files_copied} files, {dirs_copied} directories")
    else:
        print_info("No CLI files to sync (template may not have CLI structure yet)")

    return True


def sync(template_path: str | Path) -> bool:
    """Synchronize template files to current project.

    Args:
        template_path: Path to python-quality-template directory

    Returns:
        True if synchronization succeeded, False otherwise
    """
    template_path = Path(template_path).resolve()
    target_path = Path(__file__).resolve().parent.parent

    if not template_path.exists():
        print_error(f"Template path does not exist: {template_path}")
        return False

    if not template_path.is_dir():
        print_error(f"Template path is not a directory: {template_path}")
        return False

    if template_path == target_path:
        print_warning("Template path and target path are the same. Skipping.")
        return False

    print_info(f"Synchronizing from: {template_path}")
    print_info(f"Target project: {target_path}")

    success = True
    success &= sync_services(template_path, target_path)
    success &= sync_service_py(template_path, target_path)
    success &= sync_cli(template_path, target_path)

    if success:
        print_success("Template synchronization completed successfully")
    else:
        print_error("Template synchronization completed with errors")

    return success


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python template.py sync <template_path>")
        print("\nCommands:")
        print("  sync <path>  Synchronize template files from python-quality-template")
        print("\nExample:")
        print("  python template.py sync /path/to/python-quality-template")
        return 1

    command = sys.argv[1].lower()

    if command == "sync":
        if len(sys.argv) < 3:
            print_error("Missing template path argument")
            print("Usage: python template.py sync <template_path>")
            return 1

        template_path = sys.argv[2]
        success = sync(template_path)
        return 0 if success else 1
    else:
        print_error(f"Unknown command: {command}")
        print("Available commands: sync")
        return 1


if __name__ == "__main__":
    sys.exit(main())

