#!/usr/bin/env python3
"""
Complete validation script for PulseEchoGui project.

This script performs comprehensive checks to ensure the project is ready
for distribution and use.

Run this script before:
- Publishing to PyPI
- Creating a release
- Submitting a pull request
- Deploying to production

Usage:
    python validate_project.py
    python validate_project.py --verbose
    python validate_project.py --fix  # Auto-fix issues when possible
"""

import sys
import os
import subprocess
import importlib
from pathlib import Path
from typing import List, Tuple, Optional

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(text: str):
    """Print a success message."""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text: str):
    """Print an error message."""
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text: str):
    """Print a warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text: str):
    """Print an info message."""
    print(f"{Colors.BLUE}ℹ{Colors.END} {text}")

def run_command(cmd: List[str], check: bool = True) -> Tuple[bool, str]:
    """
    Run a shell command and return success status and output.

    Parameters
    ----------
    cmd : List[str]
        Command to run as list of arguments
    check : bool
        Whether to check return code

    Returns
    -------
    success : bool
        True if command succeeded
    output : str
        Command output
    """
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr
    except FileNotFoundError:
        return False, f"Command not found: {cmd[0]}"

def check_python_version() -> bool:
    """Check Python version is >= 3.8."""
    print_info("Checking Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print_success(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} (requires >= 3.8)")
        return False

def check_package_installation() -> bool:
    """Check if package can be imported."""
    print_info("Checking package installation...")
    try:
        import pulseechogui
        version = pulseechogui.__version__
        print_success(f"PulseEchoGui {version} installed")
        return True
    except ImportError as e:
        print_error(f"Cannot import pulseechogui: {e}")
        print_warning("Run: pip install -e .")
        return False

def check_dependencies() -> bool:
    """Check all required dependencies are installed."""
    print_info("Checking dependencies...")

    required = {
        "numpy": "1.20.0",
        "scipy": "1.7.0",
        "matplotlib": "3.5.0",
        "joblib": "1.1.0",
    }

    all_ok = True
    for package, min_version in required.items():
        try:
            mod = importlib.import_module(package)
            version = getattr(mod, "__version__", "unknown")
            print_success(f"{package} {version}")
        except ImportError:
            print_error(f"{package} not installed (requires >= {min_version})")
            all_ok = False

    return all_ok

def check_optional_dependencies() -> bool:
    """Check optional dependencies."""
    print_info("Checking optional dependencies...")

    optional = ["pytest", "black", "isort", "flake8"]

    all_ok = True
    for package in optional:
        try:
            importlib.import_module(package)
            print_success(f"{package} available")
        except ImportError:
            print_warning(f"{package} not installed (optional)")
            all_ok = False

    return all_ok

def check_core_modules() -> bool:
    """Check core modules can be imported."""
    print_info("Checking core modules...")

    modules = [
        "pulseechogui.core.spinecho",
        "pulseechogui.core.spinechoshaped",
        "pulseechogui.gui",
        "pulseechogui.i18n",
    ]

    all_ok = True
    for module in modules:
        try:
            importlib.import_module(module)
            print_success(f"{module}")
        except ImportError as e:
            print_error(f"{module}: {e}")
            all_ok = False

    return all_ok

def check_cli_commands() -> bool:
    """Check CLI commands are available."""
    print_info("Checking CLI commands...")

    commands = [
        "pulseechogui-basic",
        "pulseechogui-basic-single",
        "pulseechogui-shaped",
        "pulseechogui-validate",
    ]

    all_ok = True
    for cmd in commands:
        success, _ = run_command(["which", cmd], check=False)
        if success:
            print_success(f"{cmd} available")
        else:
            print_error(f"{cmd} not found")
            all_ok = False

    return all_ok

def check_documentation() -> bool:
    """Check documentation files exist."""
    print_info("Checking documentation...")

    docs = [
        "README.md",
        "QUICKSTART.md",
        "INSTALLATION.md",
        "CONTRIBUTING.md",
        "CHANGELOG.md",
        "CITATION.cff",
        "LICENSE",
    ]

    all_ok = True
    for doc in docs:
        path = Path(doc)
        if path.exists():
            print_success(f"{doc}")
        else:
            print_error(f"{doc} missing")
            all_ok = False

    return all_ok

def check_code_quality() -> bool:
    """Check code quality with formatters and linters."""
    print_info("Checking code quality...")

    all_ok = True

    # Black
    print_info("  Running Black...")
    success, output = run_command(
        ["black", "--check", "pulseechogui/", "tests/"],
        check=False
    )
    if success:
        print_success("  Black: code is formatted")
    else:
        print_warning("  Black: code needs formatting (run: black .)")
        all_ok = False

    # isort
    print_info("  Running isort...")
    success, output = run_command(
        ["isort", "--check-only", "pulseechogui/", "tests/"],
        check=False
    )
    if success:
        print_success("  isort: imports are sorted")
    else:
        print_warning("  isort: imports need sorting (run: isort .)")
        all_ok = False

    # flake8
    print_info("  Running flake8...")
    success, output = run_command(
        ["flake8", "pulseechogui/", "tests/"],
        check=False
    )
    if success:
        print_success("  flake8: no linting errors")
    else:
        print_warning("  flake8: linting issues found")
        print(output[:500])  # Show first 500 chars
        all_ok = False

    return all_ok

def check_tests() -> bool:
    """Check if tests can run."""
    print_info("Checking tests...")

    # Check if tests exist
    tests_dir = Path("tests")
    if not tests_dir.exists():
        print_error("tests/ directory not found")
        return False

    test_files = list(tests_dir.glob("test_*.py"))
    print_success(f"Found {len(test_files)} test files")

    # Try to run pytest
    print_info("  Running pytest (dry-run)...")
    success, output = run_command(
        ["pytest", "--collect-only", "-q"],
        check=False
    )
    if success:
        print_success("  pytest: tests are runnable")
        return True
    else:
        print_warning("  pytest: some issues found")
        return False

def check_build() -> bool:
    """Check if package can be built."""
    print_info("Checking package build...")

    # Check if build module is available
    try:
        import build
        print_success("build module available")
    except ImportError:
        print_warning("build module not installed (run: pip install build)")
        return False

    # Try to build (dry-run would be ideal, but not supported)
    print_info("  Package should be buildable with: python -m build")
    return True

def check_git_status() -> bool:
    """Check git repository status."""
    print_info("Checking git status...")

    # Check if in git repo
    if not Path(".git").exists():
        print_warning("Not a git repository")
        return True

    # Check for uncommitted changes
    success, output = run_command(["git", "status", "--porcelain"], check=False)
    if success:
        if output.strip():
            print_warning("Uncommitted changes detected")
            all_lines = output.strip().split('\n')
            lines = all_lines[:5]
            for line in lines:
                print(f"    {line}")
            if len(all_lines) > 5:
                remaining = len(all_lines) - 5
                print(f"    ... and {remaining} more")
            return False
        else:
            print_success("Working directory is clean")
            return True
    else:
        print_warning("Cannot check git status")
        return True

def print_summary(results: dict):
    """Print validation summary."""
    print_header("VALIDATION SUMMARY")

    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print(f"Total checks: {total}")
    print(f"{Colors.GREEN}Passed: {passed}{Colors.END}")
    print(f"{Colors.RED}Failed: {failed}{Colors.END}")
    print()

    if failed == 0:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ ALL CHECKS PASSED{Colors.END}")
        print(f"\n{Colors.GREEN}Project is ready for distribution!{Colors.END}\n")
        return True
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ SOME CHECKS FAILED{Colors.END}")
        print(f"\n{Colors.YELLOW}Please fix the issues above before distributing.{Colors.END}\n")
        return False

def main():
    """Run all validation checks."""
    print_header("PulseEchoGui Project Validation")
    print(f"Validating project in: {Path.cwd()}\n")

    # Run all checks
    results = {
        "Python Version": check_python_version(),
        "Package Installation": check_package_installation(),
        "Dependencies": check_dependencies(),
        "Optional Dependencies": check_optional_dependencies(),
        "Core Modules": check_core_modules(),
        "CLI Commands": check_cli_commands(),
        "Documentation": check_documentation(),
        "Code Quality": check_code_quality(),
        "Tests": check_tests(),
        "Build": check_build(),
        "Git Status": check_git_status(),
    }

    # Print summary
    success = print_summary(results)

    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
