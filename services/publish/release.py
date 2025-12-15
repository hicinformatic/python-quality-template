# pylint: disable=R0801  # Duplicate code acceptable for common imports
"""Release management for Git, PyPI, and other platforms."""

from __future__ import annotations

import platform
import subprocess
from typing import TYPE_CHECKING, Any

from services import utils
from services.dev.build import task_build

if TYPE_CHECKING:
    from pathlib import Path

# Use common imports from publish.common
from services.publish import common

# Import from common
# pylint: disable=R0801  # Duplicate code acceptable for common imports
PROJECT_ROOT = common.PROJECT_ROOT
print_info = common.print_info
print_success = common.print_success
print_error = common.print_error
print_warning = common.print_warning
print_header = common.print_header
print_separator = common.print_separator

# Import additional utils not in common
VENV_BIN = utils.VENV_BIN
PYTHON = utils.PYTHON
PIP = utils.PIP
venv_exists = utils.venv_exists
run_command = utils.run_command


def find_pyproject_toml() -> Path | None:
    """Find pyproject.toml file in project root.

    Note: The template provides pyproject-djangoapp.toml and pyproject-lib.toml
    as examples. Developers should rename the appropriate one to pyproject.toml
    at the project root.
    """
    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if pyproject_path.exists():
        return pyproject_path
    return None


def _check_is_django(dependencies: list[str]) -> bool:
    """Check if Django is in dependencies."""
    if not dependencies:
        return False
    deps_str = " ".join(str(dep).lower() for dep in dependencies)
    return "django" in deps_str


def _parse_project_info_with_tomli(pyproject_path: Path) -> dict[str, Any] | None:
    """Parse project info using tomli library."""
    try:
        import tomli

        with open(pyproject_path, "rb") as f:
            data = tomli.load(f)

        project_data = data.get("project", {})
        dependencies = project_data.get("dependencies", [])

        return {
            "version": project_data.get("version"),
            "name": project_data.get("name"),
            "description": project_data.get("description"),
            "is_django": _check_is_django(dependencies),
            "has_src_layout": (PROJECT_ROOT / "src").exists() and (PROJECT_ROOT / "src").is_dir(),
        }
    except ImportError:
        return None
    except Exception as e:
        print_error(f"Error reading pyproject.toml with tomli: {e}")
        return None


def _parse_project_info_fallback(pyproject_path: Path) -> dict[str, Any] | None:
    """Fallback parsing without tomli."""
    try:
        with open(pyproject_path, encoding="utf-8") as f:
            content = f.read()

        version = None
        name = None
        is_django = "Django" in content or "django" in content.lower()

        for line in content.split("\n"):
            line = line.strip()
            if line.startswith("version") and "=" in line:
                parts = line.split("=")
                if len(parts) == 2:
                    version = parts[1].strip().strip('"').strip("'")
            elif line.startswith("name") and "=" in line:
                parts = line.split("=")
                if len(parts) == 2:
                    name = parts[1].strip().strip('"').strip("'")

        return {
            "version": version,
            "name": name,
            "description": None,
            "is_django": is_django,
            "has_src_layout": (PROJECT_ROOT / "src").exists() and (PROJECT_ROOT / "src").is_dir(),
        }
    except Exception:
        return None


def get_project_info() -> dict[str, Any] | None:
    """Get project information from pyproject.toml.

    The template provides pyproject-djangoapp.toml and pyproject-lib.toml as examples.
    Developers should rename the appropriate one to pyproject.toml at the project root.
    """
    pyproject_path = find_pyproject_toml()
    if not pyproject_path:
        return None

    result = _parse_project_info_with_tomli(pyproject_path)
    if result is not None:
        return result

    return _parse_project_info_fallback(pyproject_path)


def get_project_version() -> str | None:
    """Get current project version from pyproject.toml."""
    info = get_project_info()
    return info.get("version") if info else None


def get_project_name() -> str | None:
    """Get project name from pyproject.toml."""
    info = get_project_info()
    return info.get("name") if info else None


def detect_project_type() -> str:
    """Detect project type (django-app, library, or unknown)."""
    info = get_project_info()
    if not info:
        return "unknown"

    if info.get("is_django"):
        return "django-app"
    elif info.get("has_src_layout"):
        return "library"
    else:
        return "library"  # Default to library if not Django


def get_git_tag(version: str | None = None) -> str | None:
    """Get or create git tag for version."""
    if not version:
        version = get_project_version()
        if not version:
            print_error("Could not determine version from pyproject.toml")
            return None

    tag = f"v{version}"

    # Check if tag already exists
    result = subprocess.run(
        ["git", "tag", "-l", tag],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    if result.returncode == 0 and result.stdout.strip():
        print_warning(f"Tag {tag} already exists")
        return tag

    return tag


def task_show_info() -> bool:
    """Display project information."""
    info = get_project_info()
    if not info:
        print_error("Could not find pyproject.toml")
        print_info("Make sure you're in a project directory with a pyproject.toml file")
        print_info("")
        print_info("If you're using this template:")
        print_info("  1. Choose your project type (Django app or Python library)")
        print_info("  2. Rename pyproject-djangoapp.toml or pyproject-lib.toml to pyproject.toml")
        print_info("  3. Remove the example you don't need (django_app_example/ or src/lib_example/)")
        return False

    print_separator()
    print_header("PROJECT INFORMATION")
    print_separator()
    print(f"Name: {info.get('name', 'N/A')}")
    print(f"Version: {info.get('version', 'N/A')}")
    print(f"Description: {info.get('description', 'N/A')}")
    print(f"Type: {detect_project_type()}")
    print(f"Has src/ layout: {info.get('has_src_layout', False)}")
    print(f"Is Django app: {info.get('is_django', False)}")
    print_separator()
    return True


def task_git_tag() -> bool:
    """Create a Git tag for the current version."""
    version = get_project_version()
    if not version:
        print_error("Could not determine version from pyproject.toml")
        pyproject_path = find_pyproject_toml()
        if not pyproject_path:
            print_error("pyproject.toml not found in project root")
            print_info("")
            print_info("If you're using this template:")
            print_info("  1. Choose your project type (Django app or Python library)")
            print_info("  2. Rename pyproject-djangoapp.toml or pyproject-lib.toml to pyproject.toml")
            print_info("  3. Remove the example you don't need (django_app_example/ or src/lib_example/)")
        return False

    tag = get_git_tag(version)
    if not tag:
        return False

    print_info(f"Creating Git tag: {tag}")

    # Check if we're on a clean working directory
    result = subprocess.run(
        ["git", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=PROJECT_ROOT,
    )
    if result.stdout.strip():
        print_warning("Working directory is not clean. Uncommitted changes detected.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != "y":
            return False

    # Create tag
    success, _ = run_command(
        ["git", "tag", "-a", tag, "-m", f"Release {version}"],
        check=False,
    )
    if not success:
        return False

    print_success(f"Tag {tag} created successfully")
    print_info("Push tags with: git push --tags")
    return True


def task_git_push_tags() -> bool:
    """Push Git tags to remote."""
    print_info("Pushing tags to remote...")
    success, _ = run_command(["git", "push", "--tags"], check=False)
    if success:
        print_success("Tags pushed successfully")
    return success


def task_upload_testpypi() -> bool:
    """Upload package to TestPyPI."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not task_build():
        return False

    print_info("Uploading to TestPyPI...")

    if not run_command([str(PIP), "install", "--upgrade", "twine"], check=False):
        return False

    twine = VENV_BIN / ("twine.exe" if platform.system() == "Windows" else "twine")
    success, _ = run_command(
        [str(twine), "upload", "--repository", "testpypi", "dist/*"],
        check=False,
    )

    if success:
        print_success("Upload to TestPyPI complete!")
        version = get_project_version()
        if version:
            print_info(
                f"Install with: pip install --index-url https://test.pypi.org/simple/ {PROJECT_ROOT.name}=={version}"
            )
    return success


def task_upload_pypi() -> bool:
    """Upload package to PyPI."""
    if not venv_exists():
        print_error("Virtual environment not found. Run 'python dev.py venv' first.")
        return False

    if not task_build():
        return False

    print_warning("WARNING: This will upload to PyPI!")
    print_warning("Make sure you have:")
    print_warning("  1. Updated version in pyproject.toml")
    print_warning("  2. Updated CHANGELOG.md")
    print_warning("  3. Run all tests and quality checks")
    input("Press Enter to continue, or Ctrl+C to cancel... ")

    print_info("Uploading to PyPI...")

    if not run_command([str(PIP), "install", "--upgrade", "twine"], check=False):
        return False

    twine = VENV_BIN / ("twine.exe" if platform.system() == "Windows" else "twine")
    success, _ = run_command([str(twine), "upload", "dist/*"], check=False)

    if success:
        print_success("Upload to PyPI complete!")
        version = get_project_version()
        if version:
            print_info(f"Install with: pip install {PROJECT_ROOT.name}=={version}")
    return success


def _check_github_cli() -> bool:
    """Check if GitHub CLI is available."""
    if not utils.check_github_cli():
        print_info("Alternatively, create release manually at: https://github.com/<owner>/<repo>/releases/new")
        return False
    return True


def _read_release_notes(version: str, tag: str) -> str:
    """Read release notes from CHANGELOG.md."""
    changelog_path = PROJECT_ROOT / "CHANGELOG.md"
    if not changelog_path.exists():
        return f"Release {version}"

    try:
        with open(changelog_path, encoding="utf-8") as f:
            content = f.read()

        start = content.find(f"## {version}") or content.find(f"## {tag}")
        if start == -1:
            return f"Release {version}"

        end = content.find("## ", start + 1)
        if end == -1:
            return content[start:].strip()

        return content[start:end].strip()
    except Exception as e:
        print_warning(f"Could not read CHANGELOG.md: {e}")
        return f"Release {version}"


def task_github_release() -> bool:
    """Create a GitHub release."""
    version = get_project_version()
    if not version:
        print_error("Could not determine version from pyproject.toml")
        return False

    tag = get_git_tag(version)
    if not tag:
        return False

    if not _check_github_cli():
        return False

    print_info(f"Creating GitHub release for {tag}...")
    notes = _read_release_notes(version, tag)

    cmd = ["gh", "release", "create", tag, "--title", f"Release {version}", "--notes", notes]
    success, _ = run_command(cmd, check=False)

    if success:
        print_success(f"GitHub release created: {tag}")
    return success


def task_full_release() -> bool:
    """Full release workflow: tag, build, upload, and create GitHub release."""
    print_separator()
    print_header("FULL RELEASE WORKFLOW")
    print_separator()

    version = get_project_version()
    if not version:
        print_error("Could not determine version from pyproject.toml")
        return False

    print_info(f"Releasing version: {version}")

    # Step 1: Create Git tag
    print("\n" + "-" * 70)
    print_info("Step 1/4: Creating Git tag")
    print("-" * 70)
    if not task_git_tag():
        print_error("Failed to create Git tag")
        return False

    # Step 2: Build package
    print("\n" + "-" * 70)
    print_info("Step 2/4: Building package")
    print("-" * 70)
    if not task_build():
        print_error("Build failed")
        return False

    # Step 3: Upload to PyPI
    print("\n" + "-" * 70)
    print_info("Step 3/4: Uploading to PyPI")
    print("-" * 70)
    if not task_upload_pypi():
        print_error("Upload to PyPI failed")
        return False

    # Step 4: Create GitHub release (optional)
    print("\n" + "-" * 70)
    print_info("Step 4/4: Creating GitHub release (optional)")
    print("-" * 70)
    response = input("Create GitHub release? (y/N): ")
    if response.lower() == "y":
        task_github_release()

    print_separator()
    print_success("Release workflow completed!")
    print_info(f"Version {version} has been released")
    print_separator()

    return True

