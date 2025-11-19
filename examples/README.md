# PulseEchoGui Examples

This directory contains practical examples demonstrating how to use PulseEchoGui for NMR/ESR pulse sequence simulations.

## 📚 Available Examples

### 1. Basic Hahn Echo (`basic_hahn_echo.py`)

**What it does:**
- Simulates a simple 2-pulse Hahn echo sequence (π/2 - τ - π - τ - echo)
- Demonstrates echo formation at t = 2τ
- Shows all magnetization components (Sx, Sy, Sz)

**Usage:**
```bash
python examples/basic_hahn_echo.py
```

**Output:**
- Console output with simulation progress
- PNG plot showing magnetization evolution
- Echo analysis (amplitude, timing, efficiency)

**Perfect for:**
- Beginners learning NMR/ESR basics
- Testing installation
- Understanding echo formation

---

### 2. Pulse Shapes Comparison (`pulse_shapes_comparison.py`)

**What it does:**
- Compares 4 different pulse shapes side-by-side:
  - Gaussian (frequency selective)
  - Square (broadband)
  - SECH (adiabatic)
  - WURST (frequency-swept)
- Analyzes efficiency of each pulse type
- Generates comparative plots

**Usage:**
```bash
python examples/pulse_shapes_comparison.py
```

**Output:**
- Comparative plots of all magnetization components
- Efficiency bar chart
- Recommendations for use cases

**Perfect for:**
- Choosing the right pulse shape for your experiment
- Understanding pulse shape characteristics
- Scientific presentations

---

## 🚀 Quick Start

### Prerequisites

Install PulseEchoGui:
```bash
pip install -e .
```

Or with all dependencies:
```bash
pip install -e ".[all]"
```

### Running Examples

From the project root:
```bash
# Run any example
python examples/basic_hahn_echo.py
python examples/pulse_shapes_comparison.py
```

### Modifying Examples

All examples are heavily commented and easy to customize:

```python
# In any example file, modify parameters:

# Echo delay
tau = 5.0  # Change this value

# Pulse shape
pulse_shape = 'gaussian'  # Try: 'sech', 'wurst', 'square'

# Simulation quality
detuning_points = 51  # Higher = more accurate but slower

# Parallelization
n_jobs = 4  # Match your CPU cores
```

## 📊 Example Output

### Basic Hahn Echo
```
Creating Hahn Echo sequence...
  Echo delay (τ): 5.0
  Pulse shape: gaussian
  Pulse duration: 1.0
✓ Sequence created with 4 operations

Running simulation...
  Linewidth: 2.0
  Detuning points: 51
  Parallel jobs: 4
✓ Simulation complete!

Results:
  Expected echo time: 10.00
  Echo amplitude: 0.4521
  Echo efficiency: 45.2%
```

### Pulse Shapes Comparison
```
PULSE SHAPES COMPARISON
======================================================================

Simulating Gaussian pulse...
  ✓ Complete
Simulating Square pulse...
  ✓ Complete
Simulating SECH (Adiabatic) pulse...
  ✓ Complete
Simulating WURST (Frequency Sweep) pulse...
  ✓ Complete

RESULTS ANALYSIS
======================================================================

Gaussian:
  Max signal amplitude: 0.4823
  Time of max signal: 5.12
  Relative efficiency: 48.2%
```

## 🎓 Learning Path

**Recommended order for learning:**

1. **Start here:** `basic_hahn_echo.py`
   - Learn the basics of echo sequences
   - Understand magnetization evolution
   - Get comfortable with the API

2. **Next:** `pulse_shapes_comparison.py`
   - Explore different pulse types
   - Understand trade-offs
   - Choose optimal pulses for your needs

## 🔧 Advanced Usage

### Creating Custom Examples

Use these examples as templates for your own simulations:

```python
from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator
import numpy as np
import matplotlib.pyplot as plt

# Your custom sequence
sequence = (ShapedPulseSequence("My Sequence")
    .add_shaped_pulse(np.pi/2, 1.0, 'gaussian')
    .add_delay(10.0)
    .add_shaped_pulse(np.pi, 1.0, 'sech', beta=5.0)
    .set_detection(dt=0.01, points=2000))

# Simulate
simulator = ShapedSpinEchoSimulator(n_jobs=4)
result = simulator.simulate_sequence(sequence, linewidth=2.0)

# Your custom analysis and plotting
plt.plot(result['time'], result['Sy'])
plt.show()
```

### Performance Tips

**For faster simulations:**
- Reduce `detuning_points` (try 31 instead of 51)
- Reduce `detection_points` (try 500 instead of 1000)
- Increase `n_jobs` to match your CPU cores

**For higher accuracy:**
- Increase `detuning_points` (try 101 or more)
- Increase `detection_points` (try 2000+)
- Use smaller `dt` (try 0.001 instead of 0.01)

### Saving Results

Add to any example:

```python
# Save data to CSV
import pandas as pd
df = pd.DataFrame(result)
df.to_csv('my_results.csv', index=False)

# Save plots
plt.savefig('my_plot.png', dpi=300, bbox_inches='tight')
```

## 📖 Documentation

For more details:
- [Main README](../README.md) - Complete package documentation
- [API Reference](../README.md#core-api-reference) - Detailed API docs
- [Physics Background](../README.md#physics-background) - Quantum mechanics details

## 🐛 Troubleshooting

### Import errors
```bash
# Make sure package is installed
pip install -e .

# Verify installation
python -c "import pulseechogui; print(pulseechogui.__version__)"
```

### Slow simulations
```python
# Reduce simulation parameters
detuning_points = 21  # Instead of 51
n_jobs = 8  # Use more cores
```

### Memory issues
```python
# Reduce detection points
detection_points = 500  # Instead of 1000
```

## 💡 Tips and Tricks

1. **Start simple**: Begin with default parameters, then adjust
2. **Compare results**: Run the comparison example to understand trade-offs
3. **Save your work**: Always save plots and data for reproducibility
4. **Experiment**: Try different pulse shapes and parameters
5. **Profile performance**: Use `time` command to measure execution

## 🤝 Contributing Examples

Have a cool example to share? We welcome contributions!

1. Create your example following the existing style
2. Add documentation and comments
3. Test thoroughly
4. Submit a pull request

See [CONTRIBUTING.md](../CONTRIBUTING.md) for details.

## 📧 Support

Questions about examples:
- Email: sylvain.bertaina@cnrs.fr
- GitHub Issues: https://github.com/sylvainbertaina/PulseSeq/issues
- Tag with "examples" label

## 📝 License

All examples are released under the MIT License, same as the main package.

---

**Happy simulating!** 🎉
