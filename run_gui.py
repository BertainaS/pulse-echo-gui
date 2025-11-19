#!/usr/bin/env python3
"""
Quick launcher script for PulseEchoGui applications.

This script provides an easy way to launch any of the GUI applications
without needing to install the package first.

Usage:
    python run_gui.py [gui_type]

    gui_type:
        basic       - Launch basic spin echo GUI (parallel processing) [default]
        single      - Launch basic spin echo GUI (single-core)
        shaped      - Launch shaped pulse explorer GUI
        help        - Show this help message

Examples:
    python run_gui.py               # Launch basic GUI (default)
    python run_gui.py basic         # Launch basic GUI (parallel)
    python run_gui.py single        # Launch basic GUI (single-core)
    python run_gui.py shaped        # Launch shaped pulse GUI
"""

import sys
import os
from pathlib import Path

# Add the package directory to Python path
package_dir = Path(__file__).parent
sys.path.insert(0, str(package_dir))


def show_help():
    """Display help message."""
    print(__doc__)


def launch_basic_gui():
    """Launch basic spin echo GUI (parallel version)."""
    print("Launching Basic Spin Echo GUI (Parallel Processing)...")
    print("This may take a moment to initialize...\n")
    try:
        from pulseechogui.gui import launch_basic_gui
        launch_basic_gui()
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install numpy scipy matplotlib joblib")
        sys.exit(1)


def launch_basic_gui_single():
    """Launch basic spin echo GUI (single-core version)."""
    print("Launching Basic Spin Echo GUI (Single-Core)...")
    print("This may take a moment to initialize...\n")
    try:
        from pulseechogui.gui import launch_basic_gui_single
        launch_basic_gui_single()
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install numpy scipy matplotlib joblib")
        sys.exit(1)


def launch_shaped_pulse_gui():
    """Launch shaped pulse explorer GUI."""
    print("Launching Shaped Pulse Explorer GUI...")
    print("This may take a moment to initialize...\n")
    try:
        from pulseechogui.gui import launch_shaped_pulse_gui
        launch_shaped_pulse_gui()
    except ImportError as e:
        print(f"Error importing GUI module: {e}")
        print("\nMake sure all dependencies are installed:")
        print("  pip install numpy scipy matplotlib joblib")
        sys.exit(1)


def main():
    """Main entry point for the launcher."""
    # Parse command line arguments
    if len(sys.argv) > 1:
        gui_type = sys.argv[1].lower()
    else:
        gui_type = "basic"  # Default to basic GUI

    # Route to appropriate GUI
    if gui_type in ["help", "-h", "--help"]:
        show_help()
    elif gui_type == "basic":
        launch_basic_gui()
    elif gui_type == "single":
        launch_basic_gui_single()
    elif gui_type == "shaped":
        launch_shaped_pulse_gui()
    else:
        print(f"Unknown GUI type: {gui_type}")
        print("Valid options: basic, single, shaped, help")
        print("Run 'python run_gui.py help' for more information")
        sys.exit(1)


if __name__ == "__main__":
    main()
