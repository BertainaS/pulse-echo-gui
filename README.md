# PulseEchoGui

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Platform](https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)](https://github.com/sylvainbertaina/PulseSeq)

**Standalone GUI applications for NMR/ESR spin echo pulse sequence simulation**

PulseEchoGui is a self-contained Python package providing graphical user interfaces for simulating Nuclear Magnetic Resonance (NMR) and Electron Spin Resonance (ESR) spin echo experiments. It includes both the core quantum mechanical simulation engine and multiple GUI applications for interactive exploration of pulse sequences.

## 📖 Documentation

- [Quick Start Guide](QUICKSTART.md)
- [Installation Guide](INSTALLATION.md)
- [Project Information](PROJECT_INFO.md)
- [Contributing Guidelines](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

---

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [GUI Applications Guide](#gui-applications-guide)
- [Core API Reference](#core-api-reference)
- [Physics Background](#physics-background)
- [Dependencies](#dependencies)
- [Package Structure](#package-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Credits](#credits)
- [Citation](#citation)

---

## Features

### Three Specialized GUI Applications

1. **Basic Spin Echo GUI (Parallel)**
   - 2-pulse Hahn echo sequences
   - 3-pulse stimulated echo sequences
   - Multi-core parallel processing for fast simulation
   - Real-time parameter modification
   - Phase cycling support

2. **Basic Spin Echo GUI (Single-Core)**
   - Same features as parallel version
   - Optimized for single-threaded execution
   - Ideal for debugging or systems with limited cores

3. **Shaped Pulse Explorer GUI**
   - Advanced pulse shape library (Gaussian, SECH, WURST, chirped, noisy)
   - Multi-axis control (independent Sx/Sy amplitudes)
   - Real-time pulse shape visualization
   - Complex sequence design
   - Background calculation threads for responsive UI

### Core Simulation Capabilities

- **Quantum mechanics**: Density matrix formalism for spin-1/2 systems
- **Pulse shapes**: Gaussian, square, SECH, WURST, chirped, and noisy pulses
- **Time evolution**: Matrix exponential-based propagation
- **Distribution averaging**: Gaussian, Lorentzian, exponential, uniform distributions
- **Parallel processing**: Joblib-based parallelization for speed
- **Validation**: Physics-based checks (unitarity, conservation laws)

---

## Installation

### Prerequisites

- Python >= 3.8
- tkinter (usually bundled with Python)

### Install from Source

```bash
# Clone or navigate to PulseEchoGui directory
cd PulseEchoGui

# Install the package
pip install .

# Or install in development mode
pip install -e .
```

### Verify Installation

```bash
# Validate all dependencies
pulseechogui-validate

# Or from Python
python -c "import pulseechogui; pulseechogui.validate_installation()"
```

---

## Quick Start

### Command Line Interface

After installation, you can launch any GUI directly from the command line:

```bash
# Launch basic spin echo GUI (parallel processing)
pulseechogui-basic

# Launch basic spin echo GUI (single-core)
pulseechogui-basic-single

# Launch shaped pulse explorer GUI
pulseechogui-shaped
```

### Python API

You can also launch GUIs programmatically:

```python
import pulseechogui

# Launch basic spin echo GUI (parallel)
pulseechogui.launch_basic_gui()

# Launch basic spin echo GUI (single-core)
pulseechogui.launch_basic_gui_single()

# Launch shaped pulse explorer
pulseechogui.launch_shaped_pulse_gui()
```

### Direct Script Execution

If you don't want to install the package, you can run GUI scripts directly:

```bash
cd PulseEchoGui/pulseechogui/gui

# Run basic GUI (parallel)
python Spin_echo_2p_3p_gui.py

# Run basic GUI (single-core)
python Spin_echo_2p_3p_single_core_gui.py

# Run shaped pulse GUI
python PulseShapedSeq_gui.py
```

---

## GUI Applications Guide

### 1. Basic Spin Echo GUI

**Features:**
- **2-pulse Hahn echo**: π/2 - τ - π - τ - echo
- **3-pulse stimulated echo**: π/2 - τ₁ - π/2 - τ₂ - π/2 - echo
- **Pulse types**: Hard (instantaneous) or soft (finite duration)
- **Parameters**:
  - Echo delay (τ)
  - Detuning (frequency offset)
  - Linewidth (Gaussian distribution)
  - Microwave amplitude
  - Phase cycling

**Usage:**
- Adjust sliders to modify parameters in real-time
- Select pulse type (hard/soft) from dropdown
- Toggle between 2-pulse and 3-pulse sequences
- Observe echo formation in the plot

### 2. Shaped Pulse Explorer GUI

**Features:**
- **Pulse shapes**:
  - **Gaussian**: Smooth amplitude envelope, frequency selective
  - **SECH**: Hyperbolic secant adiabatic pulse
  - **WURST**: Wideband uniform rate smooth truncation
  - **Chirped**: Linear frequency sweep with various envelopes
  - **Noisy**: Realistic experimental pulse with fluctuations

- **Shape-specific parameters**:
  - Gaussian: `sigma_factor` (envelope width)
  - SECH: `beta` (adiabaticity parameter)
  - WURST: `freq_start`, `freq_end`, `wurst_n` (sweep parameters)
  - Chirp: `freq_start`, `freq_end`, envelope type
  - Noisy: base shape, amplitude/phase noise levels, random seed

- **Multi-axis control**: Independent Sx and Sy amplitude scaling

**Usage:**
- Select pulse shape from dropdown
- Adjust shape-specific parameters
- Set pulse duration, flip angle, and echo delay
- Visualize pulse shape in real-time
- Simulate complete echo sequence

---

## Core API Reference

### Creating Custom Sequences

You can use the core simulation API to build custom sequences programmatically:

#### Using the Shaped Pulse Framework

```python
from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator
import numpy as np

# Build a sequence
sequence = (ShapedPulseSequence("My Sequence")
    .add_shaped_pulse(np.pi/2, 1.0, 'gaussian', sigma_factor=3.0)
    .add_delay(5.0)
    .add_shaped_pulse(np.pi, 1.0, 'sech', beta=5.0)
    .add_delay(5.0)
    .set_detection(dt=0.01, points=1000)
    .set_multi_axis(sx_amp=1.0, sy_amp=0.8))

# Run simulation
simulator = ShapedSpinEchoSimulator(n_jobs=4)
signals = simulator.simulate_sequence(
    sequence,
    linewidth=2.0,
    distribution='gaussian',
    detuning_points=51
)

# Plot results
import matplotlib.pyplot as plt
plt.plot(signals['time'], signals['Sx'])
plt.xlabel('Time')
plt.ylabel('Signal (Sx)')
plt.show()
```

#### Using the Flexible Sequence Framework

```python
from pulseechogui import SequenceBuilder, PulseParameters, DelayParameters
import numpy as np

# Build a sequence
builder = SequenceBuilder()
sequence = (builder
    .add_pulse(PulseParameters(flip_angle=np.pi/2, phase=0.0))
    .add_delay(DelayParameters(duration=5.0))
    .add_pulse(PulseParameters(flip_angle=np.pi, phase=0.0))
    .build())
```

### Available Pulse Shapes

```python
from pulseechogui import PulseShapeFactory

# Create pulse shape generator
factory = PulseShapeFactory()

# Generate various pulse shapes
gaussian_pulse = factory.create('gaussian', duration=2.0, sigma_factor=3.0)
sech_pulse = factory.create('sech', duration=2.0, beta=5.0)
wurst_pulse = factory.create('wurst', duration=2.0, freq_start=-10, freq_end=10, wurst_n=2)
chirp_pulse = factory.create('chirped', duration=2.0, freq_start=-5, freq_end=5, envelope='gaussian')
```

---

## Physics Background

### Quantum Mechanical Framework

**Density Matrix Formalism:**
- State: ρ = |ψ⟩⟨ψ| for pure states
- Evolution: ρ(t) = U(t)·ρ(0)·U†(t)
- Observable: ⟨A⟩ = Tr(ρ·A)

**Pauli Matrices (factor of ½ convention):**
- Sₓ = ½σₓ, Sᵧ = ½σᵧ, Sᵤ = ½σᵤ

**Hamiltonian:**
- Hard pulse: H = θ·S_φ
- Soft pulse: H = ω₁·S_φ + δ·Sᵤ
- Free evolution: H = δ·Sᵤ

where S_φ = cos(φ)·Sₓ + sin(φ)·Sᵧ

### Typical Parameter Ranges

- **Flip angles**: π/2 (90°), π (180°)
- **Echo delays**: τ ∈ [1, 10] time units
- **Pulse duration**: 0.5-3.0 time units (shaped pulses)
- **Detuning**: δ ∈ [-10, 10] frequency units
- **Linewidth**: σ ∈ [1, 3] (Gaussian)
- **Distribution points**: 31-101 (accuracy vs speed)

---

## Dependencies

### Required

- **numpy** >= 1.20.0: Numerical arrays and matrix operations
- **scipy** >= 1.7.0: Matrix exponential (expm) for quantum evolution
- **matplotlib** >= 3.5.0: Visualization and plotting
- **joblib** >= 1.1.0: Parallel processing
- **tkinter**: GUI framework (usually bundled with Python)

### Optional

- **dev tools**: pytest, black, isort, flake8 (for development)

---

## Package Structure

```
PulseEchoGui/
├── README.md                   # This file
├── setup.py                    # Legacy setup script
├── pyproject.toml              # Modern Python packaging
├── run_gui.py                  # Quick launcher script
└── pulseechogui/               # Main package
    ├── __init__.py             # Package entry point
    ├── core/                   # Core simulation modules
    │   ├── __init__.py
    │   ├── spinecho.py         # Flexible sequence framework
    │   └── spinechoshaped.py   # Shaped pulse framework
    └── gui/                    # GUI applications
        ├── __init__.py
        ├── Spin_echo_2p_3p_gui.py              # Basic GUI (parallel)
        ├── Spin_echo_2p_3p_single_core_gui.py  # Basic GUI (single-core)
        └── PulseShapedSeq_gui.py               # Shaped pulse explorer
```

---

## Development

### Code Quality

This package follows strict Python best practices:

- **Formatting**: Black (line length 88)
- **Import sorting**: isort
- **Linting**: flake8
- **Type hints**: Python 3.8+ compatible

### Run Development Tools

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Format code
black pulseechogui/
isort pulseechogui/

# Lint code
flake8 pulseechogui/
```

---

## Troubleshooting

### Import Errors

If you encounter import errors after installation:

```bash
# Validate installation
pulseechogui-validate

# Check Python path
python -c "import pulseechogui; print(pulseechogui.__file__)"

# Reinstall in development mode
pip uninstall pulseechogui
pip install -e .
```

### tkinter Not Found

If tkinter is missing (rare on macOS/Windows, possible on Linux):

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# macOS (should be bundled)
# Reinstall Python from python.org if needed
```

### Performance Issues

For slow simulations:

- Reduce `detuning_points` (e.g., from 101 to 31)
- Decrease `n_time_slices` for shaped pulses
- Use single-core GUI for simpler debugging
- Close other applications to free system resources

---

## License

MIT License - see parent PulseSeq project for details.

---

## Credits

**Author**: Sylvain Bertaina
**Email**: sylvain.bertaina@cnrs.fr
**Institution**: CNRS (Centre National de la Recherche Scientifique)

Part of the **PulseSeq** project: https://github.com/sylvainbertaina/PulseSeq

---

## Citation

If you use this software in your research, please cite:

```
Bertaina, S. (2024). PulseSeq: Comprehensive framework for NMR/ESR pulse sequence simulation.
https://github.com/sylvainbertaina/PulseSeq
```

---

## See Also

- **Full PulseSeq package**: Complete framework with examples, notebooks, and documentation
- **Shaped Pulse Tutorial**: Comprehensive guide to advanced pulse shapes
- **Example scripts**: Demonstrations and benchmarks in the main PulseSeq repository
