# PulseEchoGui - Project Information

## Overview

**PulseEchoGui** is a standalone sub-project extracted from **PulseSeq**, containing only the GUI applications for simulating NMR/ESR spin echo sequences.

## Package Contents

### Core Modules (`pulseechogui/core/`)

1. **spinecho.py** (14,986 bytes)
   - Flexible framework for sequence construction
   - Classes: `SequenceBuilder`, `PulseParameters`, `DelayParameters`, `SpinEchoSimulator`

2. **spinechoshaped.py** (40,609 bytes)
   - Advanced framework for pulses with complex shapes
   - Classes: `ShapedPulseSequence`, `ShapedSpinEchoSimulator`, `PulseShapeFactory`
   - Pulse shapes: Gaussian, SECH, WURST, Chirped, Noisy

### GUI Applications (`pulseechogui/gui/`)

1. **Spin_echo_2p_3p_gui.py** (45,776 bytes)
   - Basic GUI for 2-pulse and 3-pulse sequences
   - Parallel version (multi-core)
   - Features: Hahn echo, stimulated echo

2. **Spin_echo_2p_3p_single_core_gui.py** (43,099 bytes)
   - Same GUI in single-core version
   - Optimized for debugging and simple systems

3. **PulseShapedSeq_gui.py** (42,825 bytes)
   - Advanced pulse explorer with shapes
   - Real-time visualization
   - Multi-axis control (Sx/Sy)

### Configuration and Documentation

- **README.md** - Complete documentation
- **QUICKSTART.md** - Quick start guide
- **INSTALLATION.md** - Installation guide
- **PROJECT_INFO.md** - Project information
- **pyproject.toml** - Modern package configuration (PEP 517/518)
- **setup.py** - Legacy configuration for compatibility
- **LICENSE** - MIT License
- **MANIFEST.in** - Files to include in distribution
- **.gitignore** - Files to exclude from version control
- **run_gui.py** - Quick launch script

## Available CLI Commands

After installation (`pip install .` or `pip install -e .`):

```bash
pulseechogui-basic           # Launch basic GUI (parallel)
pulseechogui-basic-single    # Launch basic GUI (single-core)
pulseechogui-shaped          # Launch advanced pulse explorer
pulseechogui-validate        # Validate installation
```

## Usage Without Installation

Via the `run_gui.py` script:

```bash
python run_gui.py           # Basic GUI (default)
python run_gui.py basic     # Basic GUI (parallel)
python run_gui.py single    # Basic GUI (single-core)
python run_gui.py shaped    # Advanced pulse GUI
python run_gui.py help      # Display help
```

## Python API

```python
import pulseechogui

# Launch a GUI
pulseechogui.launch_basic_gui()
pulseechogui.launch_basic_gui_single()
pulseechogui.launch_shaped_pulse_gui()

# Use simulation classes
from pulseechogui import (
    ShapedPulseSequence,
    ShapedSpinEchoSimulator,
    SequenceBuilder,
    PulseParameters
)

# Create a sequence
seq = ShapedPulseSequence("Test").add_shaped_pulse(np.pi/2, 1.0, 'gaussian')
```

## Dependencies

### Required
- numpy >= 1.20.0
- scipy >= 1.7.0
- matplotlib >= 3.5.0
- joblib >= 1.1.0
- tkinter (usually bundled with Python)

### Optional
- pytest >= 6.0 (dev)
- black >= 22.0 (dev)
- isort >= 5.10 (dev)
- flake8 >= 4.0 (dev)

## File Structure

```
PulseEchoGui/
├── PROJECT_INFO.md          # This file
├── README.md                # Complete documentation
├── QUICKSTART.md            # Quick start guide
├── INSTALLATION.md          # Installation guide
├── LICENSE                  # MIT License
├── MANIFEST.in              # Distribution manifest
├── .gitignore               # Files to ignore
├── pyproject.toml           # Modern configuration
├── setup.py                 # Legacy configuration
├── run_gui.py               # Quick launch script
└── pulseechogui/            # Main package
    ├── __init__.py          # Entry point (exports, version)
    ├── core/                # Simulation engines
    │   ├── __init__.py
    │   ├── spinecho.py
    │   └── spinechoshaped.py
    └── gui/                 # GUI applications
        ├── __init__.py
        ├── Spin_echo_2p_3p_gui.py
        ├── Spin_echo_2p_3p_single_core_gui.py
        └── PulseShapedSeq_gui.py
```

## Project Size

- **Total code**: ~147 KB
- **Python files**: 8 files
- **Lines of code**: ~3,100 lines (estimate)

## Installation and Testing

### Development mode installation

```bash
cd PulseEchoGui
pip install -e .
```

### Installation test

```bash
pulseechogui-validate
```

### Import test

```python
python -c "import pulseechogui; print(pulseechogui.__version__)"
```

## Differences from PulseSeq (Parent Project)

### Included in PulseEchoGui
✓ Core simulation modules (spinecho, spinechoshaped)
✓ GUI applications
✓ CLI commands to launch GUIs
✓ Usage documentation

### Not included in PulseEchoGui
✗ Example scripts
✗ Jupyter notebooks
✗ Benchmarks
✗ Unit tests
✗ Sphinx documentation
✗ Advanced tutorials

## Use Cases

**Use PulseEchoGui if:**
- You only want the graphical interfaces
- You need a lightweight package
- You're developing an application that uses the GUIs

**Use PulseSeq (parent) if:**
- You want all examples and tutorials
- You're developing new algorithms
- You need educational notebooks
- You want to contribute to the project

## Support and Contribution

- **Author**: Sylvain Bertaina
- **Email**: sylvain.bertaina@cnrs.fr
- **Institution**: CNRS
- **Parent project**: https://github.com/sylvainbertaina/PulseSeq
- **Issues**: https://github.com/sylvainbertaina/PulseSeq/issues

## License

MIT License - See LICENSE file for details.

## Version

**Current version**: 1.0.0 (2024)

## History

- **2024-11**: Creation of PulseEchoGui sub-project
- Extraction of GUI modules from PulseSeq
- Standalone package with minimal dependencies
- Complete documentation and launch scripts

## Validation

✓ Package installable via pip
✓ All CLI commands functional
✓ Python imports working correctly
✓ Dependency validation functional
✓ Clean modular structure
✓ Complete documentation

## Technical Notes

### Code Conventions
- Format: Black (max line 88)
- Import sorting: isort
- Linting: flake8
- Type hints: Python 3.8+

### Physics
- Formalism: Density matrices
- Spin: 1/2
- Pauli matrices: Factor 0.5 convention
- Evolution: Matrix exponential (scipy.linalg.expm)

### Performance
- Parallelization: joblib (configurable n_jobs)
- Optimization: NumPy vectorization
- GUI threading: Background calculations

---

**Creation date**: November 2, 2024
**Last updated**: November 2, 2024
