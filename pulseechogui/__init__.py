"""
PulseEchoGui - GUI Applications for Spin Echo Simulations

A standalone package providing graphical user interfaces for simulating
Nuclear Magnetic Resonance (NMR) and Electron Spin Resonance (ESR) pulse sequences.

This package includes:
- Core simulation engines for quantum mechanical evolution
- Multiple GUI applications for different pulse sequence types
- Real-time visualization and parameter exploration
- Support for basic and advanced pulse shapes

Quick Start
-----------
>>> import pulseechogui
>>> pulseechogui.launch_basic_gui()  # Launch basic spin echo GUI
>>> pulseechogui.launch_shaped_pulse_gui()  # Launch shaped pulse GUI

CLI Commands (after installation)
----------------------------------
pulseechogui-basic       - Launch basic spin echo GUI (parallel)
pulseechogui-basic-single - Launch basic spin echo GUI (single-core)
pulseechogui-shaped      - Launch shaped pulse explorer GUI
"""

__version__ = "1.0.0"
__author__ = "Sylvain Bertaina"
__email__ = "sylvain.bertaina@cnrs.fr"

# Import core simulation modules
from .core import (
    ShapedPulseSequence,
    ShapedSpinEchoSimulator,
    PulseShapeFactory,
    plot_pulse_shape,
    SequenceBuilder,
    PulseParameters,
    DelayParameters,
    DetectionParameters,
)

# Import GUI launchers
from .gui import (
    launch_basic_gui,
    launch_basic_gui_single,
    launch_shaped_pulse_gui,
)

__all__ = [
    # Version info
    '__version__',
    '__author__',
    '__email__',

    # Core simulation classes
    'ShapedPulseSequence',
    'ShapedSpinEchoSimulator',
    'PulseShapeFactory',
    'plot_pulse_shape',
    'SequenceBuilder',
    'PulseParameters',
    'DelayParameters',
    'DetectionParameters',

    # GUI launchers
    'launch_basic_gui',
    'launch_basic_gui_single',
    'launch_shaped_pulse_gui',
]

def get_version():
    """Return the version of PulseEchoGui."""
    return __version__

def validate_installation():
    """
    Validate that all required dependencies are installed.

    Returns
    -------
    bool
        True if all dependencies are available

    Raises
    ------
    ImportError
        If a required dependency is missing
    """
    required = ['numpy', 'scipy', 'matplotlib', 'joblib']
    missing = []

    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        raise ImportError(
            f"Missing required packages: {', '.join(missing)}\n"
            f"Install with: pip install {' '.join(missing)}"
        )

    print("✓ All required dependencies are installed")
    print(f"✓ PulseEchoGui version {__version__}")
    return True
