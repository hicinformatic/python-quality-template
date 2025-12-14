#!/usr/bin/env python3
"""Template synchronization service.

Synchronizes template files from python-quality-template to target projects.
"""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

# Add parent directory to path for absolute imports
_services_dir = Path(__file__).resolve().parent
_project_root = _services_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

# Use absolute imports after adding to path
from services import utils

print_info = utils.print_info
print_success = utils.print_success
print_error = utils.print_error
print_warning = utils.print_warning


def sync_services(template_path: Path, target_path: Path) -> bool:
    """Sync .services/* files from template to target project."""
    template_services = template_path / ".services"
    target_services = target_path / ".services"

    if not template_services.exists():
        print_error(f"Template .services directory not found: {template_services}")
        return False

    if not target_services.exists():
        target_services.mkdir(parents=True, exist_ok=True)
        print_info(f"Created .services directory: {target_services}")

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

    print_success(f"Synced .services: {files_copied} files, {dirs_copied} directories")
    return True


def sync_service_py(template_path: Path, target_path: Path) -> bool:
    """Sync service.py from template to target project."""
    template_service = template_path / "service.py"
    target_service = target_path / "service.py"

    if not template_service.exists():
        print_error(f"Template service.py not found: {template_service}")
        return False

    shutil.copy2(template_service, target_service)
    print_success(f"Synced service.py")
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

