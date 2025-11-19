# PulseEchoGui - Installation and Usage Guide

## 📋 Overview

**PulseEchoGui** is a standalone Python package containing graphical user interfaces (GUIs) for simulating spin echo sequences in NMR/ESR. It has been extracted from the parent project **PulseSeq** to facilitate installation and usage of GUI tools.

## ✅ What Has Been Created

### Project Structure

```
PulseEchoGui/
├── 📄 README.md                    # Complete documentation (English)
├── 📄 QUICKSTART_EN.md             # Quick start (English)
├── 📄 QUICKSTART.md                # Quick start (French)
├── 📄 INSTALLATION.md              # This file (English)
├── 📄 INSTALLATION_FR.md           # Installation guide (French)
├── 📄 PROJECT_INFO_EN.md           # Detailed project information (English)
├── 📄 PROJECT_INFO.md              # Detailed project information (French)
├── 📄 LICENSE                      # MIT License
├── 📄 pyproject.toml               # Package configuration
├── 📄 setup.py                     # Installation script
├── 📄 MANIFEST.in                  # Distribution manifest
├── 📄 .gitignore                   # Files to ignore
├── 🐍 run_gui.py                   # Quick launch script
│
└── 📦 pulseechogui/                # Main package
    ├── 📄 __init__.py              # Package entry point
    │
    ├── 📁 core/                    # Simulation engines
    │   ├── __init__.py
    │   ├── spinecho.py             # Flexible framework
    │   └── spinechoshaped.py       # Advanced pulse framework
    │
    └── 📁 gui/                     # GUI applications
        ├── __init__.py
        ├── Spin_echo_2p_3p_gui.py          # Basic GUI (parallel)
        ├── Spin_echo_2p_3p_single_core_gui.py  # Basic GUI (single-core)
        └── PulseShapedSeq_gui.py           # Advanced pulse GUI
```

## 🚀 Installation

### Method 1: Standard Installation

```bash
cd PulseEchoGui
pip install .
```

### Method 2: Development Mode Installation

```bash
cd PulseEchoGui
pip install -e .
```

This method is recommended if you plan to modify the code.

### Installation Verification

```bash
# Via CLI command
pulseechogui-validate

# Via Python
python -c "import pulseechogui; pulseechogui.validate_installation()"
```

You should see:
```
✓ All required dependencies are installed
✓ PulseEchoGui version 1.0.0
```

## 🎮 Usage

### Option 1: CLI Commands (After Installation)

After installation, four CLI commands are available:

```bash
# Launch basic GUI with parallel processing
pulseechogui-basic

# Launch basic GUI in single-core mode
pulseechogui-basic-single

# Launch advanced pulse explorer
pulseechogui-shaped

# Validate installation
pulseechogui-validate
```

### Option 2: Python Script (Without Installation)

If you don't want to install the package, use the `run_gui.py` script:

```bash
# Basic GUI (default)
python run_gui.py

# Or specify explicitly
python run_gui.py basic      # Basic GUI (parallel)
python run_gui.py single     # Basic GUI (single-core)
python run_gui.py shaped     # Advanced pulse GUI
python run_gui.py help       # Display help
```

### Option 3: Python Import

```python
import pulseechogui

# Launch a GUI
pulseechogui.launch_basic_gui()          # Basic GUI (parallel)
pulseechogui.launch_basic_gui_single()   # Basic GUI (single-core)
pulseechogui.launch_shaped_pulse_gui()   # Advanced pulse GUI
```

## 📚 The Three GUI Applications

### 1. Basic GUI (Parallel) - `pulseechogui-basic`

**Features:**
- Hahn echo sequences (2 pulses): π/2 - τ - π - τ - echo
- Stimulated echo sequences (3 pulses): π/2 - τ₁ - π/2 - τ₂ - π/2 - echo
- Multi-core parallel processing for fast simulations
- Real-time parameter modification
- Phase cycling support

**When to use:**
- Fast simulations with parallelized calculations
- Systems with multiple CPU cores
- Standard echo sequences

### 2. Basic GUI (Single-Core) - `pulseechogui-basic-single`

**Features:**
- Same functionality as parallel version
- Optimized for single-core execution
- Simpler for debugging

**When to use:**
- Debugging simulations
- Systems with limited CPUs
- Need for sequential traceability

### 3. Advanced Pulse GUI - `pulseechogui-shaped`

**Features:**
- **Available pulse shapes:**
  - **Gaussian**: Smooth envelope, frequency selective
  - **SECH**: Adiabatic hyperbolic secant pulse
  - **WURST**: Wideband uniform rate smooth truncation
  - **Chirped**: Linear frequency sweep
  - **Noisy**: Realistic pulse with fluctuations

- **Advanced controls:**
  - Shape-specific parameters
  - Multi-axis control (independent Sx/Sy amplitudes)
  - Real-time shape visualization
  - Complex sequence design

**When to use:**
- Exploring advanced pulse shapes
- Frequency sweep simulations
- Precise RF amplitude control
- Adiabatic pulse studies

## 🔧 Programmatic Usage

### Example 1: Simple Sequence

```python
from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator
import numpy as np
import matplotlib.pyplot as plt

# Create a Hahn echo sequence with Gaussian pulses
sequence = (ShapedPulseSequence("Hahn Echo")
    .add_shaped_pulse(np.pi/2, 1.0, 'gaussian')  # π/2 pulse
    .add_delay(5.0)                               # Delay τ
    .add_shaped_pulse(np.pi, 1.0, 'gaussian')     # π pulse
    .add_delay(5.0)                               # Delay τ
    .set_detection(dt=0.01, points=1000))         # Detection

# Simulate
simulator = ShapedSpinEchoSimulator(n_jobs=4)
result = simulator.simulate_sequence(
    sequence,
    linewidth=2.0,
    distribution='gaussian',
    detuning_points=51
)

# Plot
plt.figure(figsize=(10, 6))
plt.plot(result['time'], result['Sx'], label='Sx')
plt.plot(result['time'], result['Sy'], label='Sy')
plt.xlabel('Time')
plt.ylabel('Signal')
plt.legend()
plt.title('Hahn Echo')
plt.grid(True)
plt.show()
```

### Example 2: WURST Pulse

```python
from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator
import numpy as np

# Sequence with WURST pulse (wideband sweep)
sequence = (ShapedPulseSequence("WURST Demo")
    .add_shaped_pulse(np.pi/2, 2.0, 'wurst')
    .add_delay(5.0)
    .set_detection(dt=0.01, points=500))

# Simulate with wide frequency distribution
simulator = ShapedSpinEchoSimulator(n_jobs=4)
result = simulator.simulate_sequence(
    sequence,
    linewidth=3.0,
    detuning_points=101  # More points for wideband
)
```

## 📦 Dependencies

### Required

```
numpy >= 1.20.0       # Numerical computations
scipy >= 1.7.0        # Matrix exponential
matplotlib >= 3.5.0   # Visualization
joblib >= 1.1.0       # Parallel processing
tkinter                # GUI (usually bundled with Python)
```

### Manual Installation (if needed)

```bash
pip install numpy scipy matplotlib joblib
```

### tkinter on Linux

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter

# Arch Linux
sudo pacman -S tk
```

## ❓ Troubleshooting

### Problem: ImportError after installation

**Solution:**
```bash
pip uninstall pulseechogui
pip install -e .
```

### Problem: tkinter not found

**Linux Solution:**
```bash
sudo apt-get install python3-tk  # Ubuntu/Debian
```

**macOS Solution:**
tkinter should be included. If missing, reinstall Python from python.org

### Problem: Slow simulations

**Solutions:**
1. Reduce `detuning_points` (from 101 to 31)
2. Use single-core version for debugging
3. Reduce number of detection points
4. Close other applications

### Problem: CLI commands not found

**Check installation:**
```bash
which pulseechogui-basic
pip show pulseechogui
```

**Reinstall:**
```bash
pip install --force-reinstall .
```

## 🔍 Testing and Validation

### Import Test

```python
python -c "import pulseechogui; print(pulseechogui.__version__)"
```

### Core Modules Test

```python
python -c "
from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator
import numpy as np
seq = ShapedPulseSequence('Test')
seq.add_shaped_pulse(np.pi/2, 1.0, 'gaussian')
print('✓ Test passed')
"
```

### Check CLI Commands

```bash
which pulseechogui-basic
which pulseechogui-shaped
which pulseechogui-validate
```

## 📖 Additional Documentation

- **README.md** - Complete documentation in English
- **QUICKSTART_EN.md** - Quick start guide (English)
- **QUICKSTART.md** - Quick start guide (French)
- **PROJECT_INFO_EN.md** - Detailed project information (English)

## 🆘 Support

**Contact:**
- Author: Sylvain Bertaina
- Email: sylvain.bertaina@cnrs.fr
- Institution: CNRS

**Parent project:**
- GitHub: https://github.com/sylvainbertaina/PulseSeq
- Issues: https://github.com/sylvainbertaina/PulseSeq/issues

## 📄 License

MIT License - See LICENSE file for details.

## ✨ Status

✅ Package installable via pip
✅ CLI commands functional
✅ Python imports working
✅ Dependency validation operational
✅ Complete documentation
✅ Tests passing

---

**Version:** 1.0.0
**Creation date:** November 2, 2024
**Last updated:** November 2, 2024
