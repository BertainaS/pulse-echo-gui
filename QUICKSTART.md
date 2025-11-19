# PulseEchoGui - Quick Start Guide

## Quick Installation

```bash
cd PulseEchoGui
pip install .
```

## Launching the GUIs

### Method 1: CLI Commands (after installation)

```bash
# Basic GUI (parallel)
pulseechogui-basic

# Basic GUI (single-core)
pulseechogui-basic-single

# GUI with advanced pulses
pulseechogui-shaped
```

### Method 2: Python Script (without installation)

```bash
# Basic GUI (default)
python run_gui.py

# Basic GUI (parallel)
python run_gui.py basic

# Basic GUI (single-core)
python run_gui.py single

# GUI with advanced pulses
python run_gui.py shaped
```

### Method 3: From Python

```python
import pulseechogui

# Launch a GUI
pulseechogui.launch_basic_gui()
pulseechogui.launch_basic_gui_single()
pulseechogui.launch_shaped_pulse_gui()
```

## Installation Verification

```bash
pulseechogui-validate
```

## Project Structure

```
PulseEchoGui/
├── README.md              # Complete documentation
├── QUICKSTART.md          # This file
├── run_gui.py             # Quick launch script
├── setup.py               # Installation
├── pyproject.toml         # Configuration
└── pulseechogui/          # Main package
    ├── core/              # Simulation modules
    │   ├── spinecho.py
    │   └── spinechoshaped.py
    └── gui/               # GUI applications
        ├── Spin_echo_2p_3p_gui.py
        ├── Spin_echo_2p_3p_single_core_gui.py
        └── PulseShapedSeq_gui.py
```

## Required Dependencies

- Python >= 3.8
- numpy >= 1.20.0
- scipy >= 1.7.0
- matplotlib >= 3.5.0
- joblib >= 1.1.0
- tkinter (bundled with Python)

## Programmatic Usage

### Simple Example with Gaussian Pulses

```python
from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator
import numpy as np
import matplotlib.pyplot as plt

# Create a sequence
seq = (ShapedPulseSequence("Test")
    .add_shaped_pulse(np.pi/2, 1.0, 'gaussian', sigma_factor=3.0)
    .add_delay(5.0)
    .add_shaped_pulse(np.pi, 1.0, 'gaussian', sigma_factor=3.0)
    .add_delay(5.0)
    .set_detection(dt=0.01, points=1000))

# Simulate
sim = ShapedSpinEchoSimulator(n_jobs=4)
result = sim.simulate_sequence(seq, linewidth=2.0, detuning_points=51)

# Display
plt.plot(result['time'], result['Sx'])
plt.xlabel('Time')
plt.ylabel('Signal (Sx)')
plt.title('Spin Echo Signal')
plt.show()
```

## Troubleshooting

### ImportError after installation

```bash
pip uninstall pulseechogui
pip install -e .
```

### tkinter not found (Linux)

```bash
# Ubuntu/Debian
sudo apt-get install python3-tk

# Fedora
sudo dnf install python3-tkinter
```

### Slow Performance

- Reduce `detuning_points` (31 instead of 101)
- Use single-core version for debugging
- Close other applications

## Complete Documentation

See `README.md` for complete documentation and advanced examples.

## Support

For issues and questions:
- Email: sylvain.bertaina@cnrs.fr
- GitHub: https://github.com/sylvainbertaina/PulseSeq/issues
