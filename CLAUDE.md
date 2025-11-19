# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
All documention, docstring and versionning must be in English
When you make documentions, commmit change, do comments never mention at any time Claude 

## Project Overview

This is a **Spin Echo Simulation** repository containing Python implementations for simulating nuclear magnetic resonance (NMR) and electron spin resonance (ESR) pulse sequences. The codebase has evolved into a comprehensive framework supporting:

- **Multiple simulation frameworks**: Basic spin echo, shaped pulses, flexible sequences
- **Advanced pulse shapes**: Gaussian, SECH, WURST, chirped, and noisy pulses
- **Multi-axis control**: Independent Sx/Sy amplitude control
- **Parallel processing**: Optimized joblib implementation
- **Interactive interfaces**: Multiple GUI applications and Jupyter notebooks
- **Comprehensive tutorials**: Step-by-step documentation and examples

---

## Scientific Python Development Guidelines

**You are an expert in computational quantum mechanics, magnetic resonance simulation, and scientific Python package development.** When working on this project, combine rigorous quantum mechanical accuracy with professional software engineering practices.

### Core Development Principles

**Package Structure and Organization:**
- Maintain clean separation between core simulation logic (`pulseseq/core/`), GUI code (`pulseseq/gui/`), examples, and documentation
- Keep modules focused: one framework per file with clear responsibilities
- Follow Python package best practices: proper `__init__.py`, relative imports, namespace management
- Organize code hierarchically: base classes → derived classes → convenience functions
- Use builder patterns for complex sequence construction (method chaining)

**Code Quality Standards:**
- Strict PEP 8 compliance enforced via Black formatter (line length 88)
- Import organization via isort (stdlib → third-party → local)
- Type hints for all public API functions (Python 3.8+ compatible)
- Comprehensive docstrings in NumPy format with mathematical notation
- Flake8 linting to catch common issues
- Use `black .` and `isort .` before committing

**Scientific Documentation:**
- Document all quantum operators with mathematical notation (LaTeX in docstrings)
- Specify Hilbert space dimensions and basis representations
- Explain physical meaning of all parameters with typical values
- Include units explicitly (radians, MHz, microseconds, dimensionless)
- Reference standard NMR/ESR textbooks for conventions
- Provide examples in docstrings showing realistic parameter ranges

**Quantum Mechanics Validation:**
- Verify density matrix properties: Tr(ρ) = 1, ρ† = ρ, eigenvalues ∈ [0,1]
- Check unitarity of evolution operators: U†U = I
- Validate conservation laws: total magnetization, coherence order
- Test commutation relations for Pauli matrices: [Sᵢ, Sⱼ] = iεᵢⱼₖSₖ
- Ensure physical observables are real: ⟨S⟩ = Tr(ρS) ∈ ℝ
- Compare with analytical solutions when available

**Performance and Scalability:**
- Use NumPy vectorization over Python loops for all array operations
- Leverage joblib parallel processing with appropriate n_jobs selection
- Profile simulation bottlenecks: matrix exponentials, distribution averaging
- Optimize time-sliced evolution: balance accuracy vs computation time
- Cache expensive computations when parameters don't change
- Use float64 precision for all quantum mechanical calculations

**Testing Philosophy:**
- Write unit tests for individual pulse operations
- Integration tests for complete sequences (Hahn echo, stimulated echo)
- Validate against known analytical results (perfect pulses, simple cases)
- Regression tests for numerical accuracy and performance
- Test edge cases: zero field, infinite linewidth, zero pulse duration
- Use pytest framework with clear test organization

### Quantum Mechanics Framework

**Density Matrix Formalism:**
- State representation: ρ = |ψ⟩⟨ψ| for pure states, statistical mixture for ensembles
- Evolution: ρ(t) = U(t)·ρ(0)·U†(t) where U = exp(-iHt)
- Observables: ⟨A⟩ = Tr(ρ·A)
- Pauli matrices: Sₓ = ½σₓ, Sᵧ = ½σᵧ, Sᵤ = ½σᵤ (factor of ½ convention)

**Hamiltonian Conventions:**
- Rotating frame Hamiltonian: H = ω₁(t)(cosφ·Sₓ + sinφ·Sᵧ) + δ·Sᵤ
- ω₁(t): Time-dependent Rabi frequency (RF amplitude)
- δ: Detuning (frequency offset from resonance)
- φ: Pulse phase (defines rotation axis in xy-plane)

**Evolution Operators:**
- Hard pulse: U = exp(-iθ·Sφ) where Sφ = cosφ·Sₓ + sinφ·Sᵧ
- Soft pulse: Integrate H(t) over pulse duration with detuning included
- Shaped pulse: Time-sliced evolution with N_slices substeps
- Free evolution: U = exp(-iδ·Sᵤ·τ) during delays

**Multi-Axis Control:**
- Independent Sx and Sy amplitude scaling for arbitrary effective fields
- Rotation axis: tan⁻¹(Aᵧ/Aₓ) from amplitude ratio
- Total field strength: √(Aₓ² + Aᵧ²) determines flip angle
- Physical interpretation: Quadrature control in experimental setups

### Physical Units and Conventions

**Standard Units in This Codebase:**
- **Time**: Dimensionless time units (typical scale: 1 unit ≈ 1 μs in real systems)
- **Frequency**: Dimensionless frequency units (detuning δ typically ±10)
- **Angles**: Radians for flip angles (π/2 ≈ 1.571, π ≈ 3.142)
- **Phase**: Radians for pulse phases (0 = +x, π/2 = +y, π = -x, 3π/2 = -y)
- **Amplitude**: Dimensionless (1.0 = perfect pulse giving exact flip angle)

**Typical Parameter Ranges:**
- Flip angles: π/2 (90°), π (180°) for standard pulses
- Echo delays: τ ∈ [1, 10] time units
- Pulse duration: 0.5-3.0 time units for shaped pulses
- Detuning range: δ ∈ [-10, 10] frequency units
- Linewidth: σ ∈ [1, 3] for Gaussian distributions
- Distribution points: 31-101 for accuracy vs speed tradeoff
- Time slices: 50-100 for shaped pulse evolution

**Phase Conventions:**
- 0° (0 rad): Pulse along +x axis
- 90° (π/2 rad): Pulse along +y axis
- 180° (π rad): Pulse along -x axis
- 270° (3π/2 rad): Pulse along -y axis
- Phase cycling: systematic variation for artifact suppression

### Pulse Sequence Conventions

**2-Pulse Hahn Echo:**
- Sequence: π/2(φ₁) - τ - π(φ₂) - τ - detect
- Echo forms at t = 2τ
- Phase cycling: [φ₁, φ₂] to remove artifacts
- Refocuses inhomogeneous broadening

**3-Pulse Stimulated Echo:**
- Sequence: π/2(φ₁) - τ₁ - π/2(φ₂) - τ₂ - π/2(φ₃) - detect
- Stimulated echo at t = τ₁ + τ₂
- Stores magnetization along z during τ₂
- Useful for long relaxation time measurements

**Shaped Pulse Sequences:**
- Gaussian: Smooth amplitude envelope, good frequency selectivity
- SECH: Adiabatic pulse for robust inversion
- WURST: Frequency-swept adiabatic pulse, broadband excitation
- Chirped: Linear frequency sweep with various envelopes
- Noisy: Realistic experimental pulse with amplitude/phase fluctuations

### Standard Code Template for New Simulation Functions

```python
"""
Brief description of the simulation functionality.

This module implements [quantum mechanical calculation] for [NMR/ESR application].

Quantum Mechanical Background:
    Hamiltonian: H = ω₁(t)(cosφ·Sx + sinφ·Sy) + δ·Sz
    Evolution: ρ(t) = U(t)·ρ(0)·U†(t)
    Observable: ⟨S⟩ = Tr(ρ·S)

References:
    - Levitt, Spin Dynamics, 2nd ed., Wiley (2008)
    - Ernst, Bodenhausen, Wokaun, NMR in One and Two Dimensions (1987)
    - Schweiger & Jeschke, Principles of Pulse EPR, Oxford (2001)

Examples:
    >>> from pulseseq import ShapedPulseSequence
    >>> seq = ShapedPulseSequence("Demo")
    >>> seq.add_shaped_pulse(np.pi/2, 1.0, 'gaussian')
    >>> seq.add_delay(5.0)
"""

import numpy as np
from scipy.linalg import expm
from typing import Tuple, Optional, Dict, Any, Union
from dataclasses import dataclass

# Pauli matrices (global constants, factor of 0.5 convention)
SX = 0.5 * np.array([[0, 1], [1, 0]], dtype=np.complex128)
SY = 0.5 * np.array([[0, -1j], [1j, 0]], dtype=np.complex128)
SZ = 0.5 * np.array([[1, 0], [0, -1]], dtype=np.complex128)

# Initial thermal equilibrium state (spin along +z)
RHO_EQ = 0.5 * np.array([[1, 0], [0, 1]], dtype=np.complex128) + SZ


@dataclass
class PulseParameters:
    """
    Parameters defining a pulse operation.
    
    Attributes
    ----------
    flip_angle : float
        Target rotation angle in radians (π/2 for 90°, π for 180°)
    phase : float
        Pulse phase in radians (0 = +x axis, π/2 = +y axis)
    duration : float
        Pulse duration in time units (0 for hard pulse)
    pulse_type : str
        "hard" (instantaneous) or "soft" (finite duration)
    amplitude : float
        Relative field strength (1.0 = perfect pulse)
    shape : str
        Pulse shape: "gaussian", "sech", "wurst", "chirped", "square"
    shape_params : dict
        Shape-specific parameters (e.g., sigma_factor, beta, freq_sweep)
        
    Notes
    -----
    For shaped pulses, duration and shape must be specified.
    Hard pulses ignore detuning effects during the pulse.
    """
    flip_angle: float
    phase: float = 0.0
    duration: float = 0.0
    pulse_type: str = "hard"
    amplitude: float = 1.0
    shape: str = "square"
    shape_params: Dict[str, Any] = None
    
    def __post_init__(self):
        """Validate parameters after initialization."""
        if not np.isfinite(self.flip_angle):
            raise ValueError(f"Invalid flip angle: {self.flip_angle}")
        if self.amplitude <= 0:
            raise ValueError(f"Amplitude must be positive: {self.amplitude}")
        if self.duration < 0:
            raise ValueError(f"Duration cannot be negative: {self.duration}")
        if self.shape_params is None:
            self.shape_params = {}


def pulse_evolution_operator(
    flip_angle: float,
    phase: float,
    pulse_type: str = "hard",
    duration: float = 0.0,
    detuning: float = 0.0,
    amplitude: float = 1.0
) -> np.ndarray:
    """
    Calculate evolution operator for a pulse.
    
    Parameters
    ----------
    flip_angle : float
        Target rotation angle in radians
    phase : float
        Pulse phase in radians (0 = +x, π/2 = +y)
    pulse_type : str
        "hard" for instantaneous or "soft" for finite duration
    duration : float
        Pulse duration in time units (only for soft pulses)
    detuning : float
        Frequency offset in dimensionless units
    amplitude : float
        Relative field strength (1.0 = perfect pulse)
        
    Returns
    -------
    U : np.ndarray, shape (2, 2)
        Evolution operator (unitary matrix)
        
    Raises
    ------
    ValueError
        If parameters are invalid
    RuntimeError
        If evolution operator is non-unitary
        
    Notes
    -----
    Hard pulse Hamiltonian: H = (amplitude·flip_angle)·S_φ
    Soft pulse Hamiltonian: H = (amplitude·ω₁)·S_φ + detuning·Sz
    where S_φ = cos(φ)·Sx + sin(φ)·Sy
    
    Evolution operator: U = exp(-i·H·t)
    
    Examples
    --------
    >>> # 90° pulse along +x axis
    >>> U_90x = pulse_evolution_operator(np.pi/2, 0.0)
    >>> 
    >>> # 180° pulse along +y axis with imperfect amplitude
    >>> U_180y = pulse_evolution_operator(np.pi, np.pi/2, amplitude=0.9)
    """
    # Input validation
    if not np.isfinite(flip_angle):
        raise ValueError(f"Invalid flip angle: {flip_angle}")
    if amplitude <= 0:
        raise ValueError(f"Amplitude must be positive: {amplitude}")
    
    # Construct rotation axis operator
    s_phi = np.cos(phase) * SX + np.sin(phase) * SY
    
    if pulse_type == "hard":
        # Instantaneous rotation, no evolution during pulse
        H = (amplitude * flip_angle) * s_phi
        U = expm(-1j * H)
        
    elif pulse_type == "soft":
        # Finite duration with detuning evolution
        if duration <= 0:
            raise ValueError(f"Soft pulse requires positive duration: {duration}")
        
        # Calculate Rabi frequency for desired flip angle
        omega1 = flip_angle / duration
        
        # Hamiltonian includes both RF and detuning
        H = amplitude * omega1 * s_phi + detuning * SZ
        U = expm(-1j * H * duration)
        
    else:
        raise ValueError(f"Unknown pulse type: {pulse_type}")
    
    # Validate unitarity (U†U = I)
    identity = np.eye(2, dtype=np.complex128)
    unitarity_check = U @ U.conj().T
    if not np.allclose(unitarity_check, identity, atol=1e-10):
        max_error = np.abs(unitarity_check - identity).max()
        raise RuntimeError(f"Non-unitary operator: max error = {max_error:.2e}")
    
    return U


def free_evolution_operator(
    duration: float,
    detuning: float
) -> np.ndarray:
    """
    Evolution operator for free precession in rotating frame.
    
    Parameters
    ----------
    duration : float
        Evolution time in time units
    detuning : float
        Frequency offset in dimensionless units
        
    Returns
    -------
    U : np.ndarray, shape (2, 2)
        Free evolution operator
        
    Notes
    -----
    Hamiltonian: H = δ·Sz (in rotating frame)
    Evolution: U(τ) = exp(-i·δ·Sz·τ)
    
    This causes phase accumulation at rate δ.
    
    Examples
    --------
    >>> # Free evolution for time τ=5 with detuning δ=2
    >>> U_free = free_evolution_operator(5.0, 2.0)
    """
    if duration < 0:
        raise ValueError(f"Duration cannot be negative: {duration}")
    
    H = detuning * SZ
    U = expm(-1j * H * duration)
    
    return U


def calculate_observable(
    rho: np.ndarray,
    operator: Union[str, np.ndarray] = "Sx"
) -> complex:
    """
    Calculate expectation value of an observable.
    
    Parameters
    ----------
    rho : np.ndarray, shape (2, 2)
        Density matrix
    operator : str or np.ndarray
        Observable operator: "Sx", "Sy", "Sz" or custom 2×2 matrix
        
    Returns
    -------
    expectation : complex
        ⟨Observable⟩ = Tr(ρ·Observable)
        
    Raises
    ------
    ValueError
        If density matrix is invalid or operator unknown
        
    Notes
    -----
    For physical observables (Sx, Sy, Sz), result should be real.
    Imaginary part indicates numerical error or non-hermitian operator.
    
    Examples
    --------
    >>> rho = SX  # State along +x
    >>> sx_value = calculate_observable(rho, "Sx")
    >>> print(f"<Sx> = {sx_value.real:.3f}")
    """
    # Validate density matrix
    trace = np.trace(rho)
    if not np.isclose(trace, 1.0, atol=1e-10):
        raise ValueError(f"Invalid density matrix trace: {trace:.6f} (should be 1.0)")
    
    # Get operator
    if isinstance(operator, str):
        ops = {"Sx": SX, "Sy": SY, "Sz": SZ}
        if operator not in ops:
            raise ValueError(f"Unknown operator: {operator}")
        op = ops[operator]
    else:
        op = operator
    
    # Calculate expectation value
    expectation = np.trace(rho @ op)
    
    # Check if result should be real
    if isinstance(operator, str) and abs(expectation.imag) > 1e-10:
        raise RuntimeError(
            f"Large imaginary part in <{operator}>: {expectation.imag:.2e}"
        )
    
    return expectation


def validate_density_matrix(rho: np.ndarray, tolerance: float = 1e-10) -> None:
    """
    Validate that a matrix represents a valid density matrix.
    
    Parameters
    ----------
    rho : np.ndarray, shape (2, 2)
        Matrix to validate
    tolerance : float
        Numerical tolerance for checks
        
    Raises
    ------
    ValueError
        If matrix violates density matrix properties
        
    Notes
    -----
    A valid density matrix must satisfy:
    1. Hermiticity: ρ† = ρ
    2. Unit trace: Tr(ρ) = 1
    3. Positive semidefinite: eigenvalues ≥ 0
    
    Examples
    --------
    >>> rho = 0.5 * (np.eye(2) + SX)  # Mixed state
    >>> validate_density_matrix(rho)  # Should pass
    """
    # Check hermiticity
    if not np.allclose(rho, rho.conj().T, atol=tolerance):
        raise ValueError("Density matrix is not Hermitian")
    
    # Check trace
    trace = np.trace(rho)
    if not np.isclose(trace, 1.0, atol=tolerance):
        raise ValueError(f"Density matrix trace is {trace:.6f}, expected 1.0")
    
    # Check positive semidefinite
    eigenvalues = np.linalg.eigvalsh(rho.real)
    if np.any(eigenvalues < -tolerance):
        raise ValueError(f"Negative eigenvalues found: {eigenvalues}")


if __name__ == "__main__":
    # Example: Simulate simple π/2 - τ - π echo sequence
    print("Simple Hahn echo simulation")
    print("="*50)
    
    # Parameters
    tau = 5.0  # Echo delay
    detuning = 2.0  # Frequency offset
    
    # Initial state (thermal equilibrium)
    rho = RHO_EQ.copy()
    print(f"Initial <Sz> = {calculate_observable(rho, 'Sz').real:.3f}")
    
    # First pulse: π/2 along +x
    U1 = pulse_evolution_operator(np.pi/2, 0.0)
    rho = U1 @ rho @ U1.conj().T
    print(f"After π/2(x): <Sy> = {calculate_observable(rho, 'Sy').real:.3f}")
    
    # Free evolution τ
    U_free = free_evolution_operator(tau, detuning)
    rho = U_free @ rho @ U_free.conj().T
    print(f"After delay τ: <Sx> = {calculate_observable(rho, 'Sx').real:.3f}")
    
    # Second pulse: π along +x (refocusing)
    U2 = pulse_evolution_operator(np.pi, 0.0)
    rho = U2 @ rho @ U2.conj().T
    
    # Second free evolution τ
    rho = U_free @ rho @ U_free.conj().T
    print(f"At echo (2τ): <Sy> = {calculate_observable(rho, 'Sy').real:.3f}")
    
    print("\nEcho formation successful!")
```

### When Creating New Features

**Planning phase:**
1. Define quantum mechanical model and approximations clearly
2. Specify coordinate system and phase conventions
3. Identify which framework is appropriate (basic/shaped/flexible)
4. Plan class hierarchy and method interfaces
5. Consider backward compatibility with existing API

**Implementation phase:**
1. Write physics calculations as pure functions first
2. Validate quantum mechanical properties (unitarity, conservation laws)
3. Add comprehensive docstrings with equations and examples
4. Use type hints for all function signatures
5. Test with analytical solutions when possible
6. Profile performance for time-critical operations

**Integration phase:**
1. Update `__init__.py` for package-level imports
2. Add CLI commands if appropriate (`setup.py` entry points)
3. Create example script demonstrating new feature
4. Update relevant documentation files
5. Add unit tests and integration tests
6. Run full validation suite (`pulseseq-validate`, `pulseseq-examples`)

**Documentation phase:**
1. Add docstrings with mathematical notation
2. Include realistic usage examples
3. Document parameter ranges and typical values
4. Update README if public API changed
5. Consider adding Jupyter notebook tutorial

### When Reviewing or Debugging Code

**Physics validation checklist:**
- Verify Pauli matrix definitions and conventions
- Check phase conventions (0 = +x, π/2 = +y)
- Validate evolution operator unitarity
- Test conservation of magnetization
- Compare with analytical results for simple cases
- Check echo formation at correct times (t = 2τ, etc.)

**Code quality checklist:**
- Run `black .` and `isort .` for formatting
- Check `flake8 .` for linting issues
- Verify type hints are present and correct
- Ensure docstrings follow NumPy format
- Test with edge cases (zero field, perfect pulses, etc.)
- Profile performance for slow operations

**Common quantum mechanics issues:**
- Phase convention errors (sign of i in exponentials)
- Unitarity violations from numerical precision
- Incorrect Hamiltonian for multi-axis pulses
- Missing detuning evolution during soft pulses
- Normalization errors in shaped pulse time slicing
- Complex conjugate errors in expectation values

**Common software issues:**
- Import order violations (use `isort`)
- Missing type hints
- Insufficient input validation
- Non-hermitian density matrices
- Memory leaks in parallel processing
- GUI thread safety (if adding GUI features)

### Integration with Existing Frameworks

**Package import patterns:**
```python
# Recommended: Use package-level imports
from pulseseq import ShapedPulseSequence, ShapedSpinEchoSimulator
from pulseseq import SequenceBuilder, PulseParameters

# Also valid: Direct core imports
from pulseseq.core.spinechoshaped import ShapedPulseSequence
from pulseseq.core.spinecho import SequenceBuilder

# Legacy scripts may use direct file imports (still works)
from spinechoshaped import ShapedPulseSequence
```

**Builder pattern for shaped sequences:**
```python
sequence = (ShapedPulseSequence("My Sequence")
    .add_shaped_pulse(np.pi/2, 1.0, 'gaussian', sigma_factor=3.0)
    .add_delay(5.0)
    .add_shaped_pulse(np.pi, 1.0, 'sech', beta=5.0)
    .add_delay(5.0)
    .set_detection(dt=0.01, points=1000)
    .set_multi_axis(sx_amp=1.0, sy_amp=0.8))
```

**Parallel simulation pattern:**
```python
simulator = ShapedSpinEchoSimulator(n_jobs=4)
signals = simulator.simulate_sequence(
    sequence,
    linewidth=2.0,
    distribution='gaussian',
    detuning_points=51
)
```

**CLI command creation:**
```python
# In setup.py or pyproject.toml
entry_points = {
    'console_scripts': [
        'pulseseq-mycommand=pulseseq.cli:my_command_function',
    ]
}
```

### Performance Optimization Guidelines

**Joblib parallelization:**
- Use `n_jobs=4` as default (good for most systems)
- Scale up to `n_jobs=8-12` for long simulations
- Set `n_jobs=1` for debugging (sequential execution)
- Monitor memory usage with many parallel jobs

**Time-sliced evolution tuning:**
- Start with `n_time_slices=50` for shaped pulses
- Increase to 100-200 if accuracy is critical
- Profile computation time vs accuracy tradeoff
- Cache pulse shape calculations when reusing

**Distribution averaging:**
- Use `detuning_points=31` for quick tests
- Standard: `detuning_points=51-71` for production
- High accuracy: `detuning_points=101` (significantly slower)
- Profile specific simulations to find optimal value

**Matrix exponential optimization:**
- SciPy's `expm` is generally optimal for 2×2 matrices
- Consider analytical formulas for simple cases (pure rotations)
- Cache evolution operators if parameters don't change

---

## Code Architecture

### Core Simulation Frameworks

**1. Basic Spin Echo (`interactive_spin_echo_2p_3p.py` and `_single_core.py`)**
- Original 2-pulse (Hahn) and 3-pulse (stimulated) echo sequences
- Hard and soft pulse implementations
- Basic spin distribution models
- GUI interface for parameter control

**2. Shaped Pulse Framework (`spinechoshaped.py`)**
- Advanced pulse shape library (Gaussian, SECH, WURST, chirped, noisy)
- Time-sliced evolution during shaped pulses
- Multi-axis evolution (Sx/Sy control)
- Sequence builder pattern with method chaining

**3. Flexible Sequence Framework (`spinecho.py`)**
- Object-oriented pulse sequence design
- Abstract base classes for extensibility
- Arbitrary pulse sequences with user-defined operations
- Clean separation of pulse parameters and evolution logic

### Key Physics Implementation

**Quantum Mechanics:**
- Density matrix formalism for spin-1/2 systems
- Pauli matrices (SX, SY, SZ) as global constants
- Evolution operators via matrix exponentials
- Time-sliced evolution for shaped pulses

**Pulse Physics:**
- **Hard pulses**: Instantaneous rotations (no evolution during pulse)
- **Soft pulses**: Finite duration with simultaneous RF and detuning evolution
- **Shaped pulses**: Arbitrary time-dependent amplitude, phase, and frequency profiles
- **Multi-axis**: Independent control of Sx and Sy components

**Advanced Features:**
- Frequency sweeps (WURST, chirped pulses)
- Noise simulation (amplitude and phase fluctuations)
- Composite pulse sequences
- Adiabatic passage techniques

### File Structure

**Core Simulation Modules:**
- **`spinechoshaped.py`**: Advanced shaped pulse simulation framework
- **`spinecho.py`**: Flexible sequence builder framework
- **`interactive_spin_echo_2p_3p.py`**: Original GUI with parallel processing
- **`interactive_spin_echo_2p_3p_single_core.py`**: Single-core optimized GUI

**GUI Applications:**
- **`tkinter_pulse_gui.py`**: Interactive shaped pulse explorer
- **`interactive_pulse_explorer.py`**: Real-time parameter modification interface

**Example Collections:**
- **`quick_examples.py`**: Fast demonstrations (~30 seconds runtime)
- **`shaped_pulse_examples.py`**: Comprehensive examples (~2-3 minutes)
- **`wurst_demo.py`**: WURST pulse specialization
- **`pulse_analysis.py`**: Quantitative pulse shape comparison

**Educational Resources:**
- **`1.ipynb`**: Original comprehensive tutorial notebook
- **`simple_hahn_echo_notebook.ipynb`**: Beginner-friendly introduction
- **`PhaseCycling.ipynb`**: Phase cycling techniques

**Benchmarking and Testing:**
- **`Benchmark.py`** and **`Benchmark.ipynb`**: Performance analysis
- **`test_*.py`**: Various testing and validation scripts

**Documentation:**
- **`SHAPED_PULSE_TUTORIAL.md`**: Complete shaped pulse guide
- **`README_EXAMPLES.md`**: Example collection overview

### Package Structure

The project is organized as a proper Python package:

```
pulseseq/
├── __init__.py              # Main package interface and convenience imports
├── core/                    # Core simulation frameworks
│   ├── spinecho.py         # Flexible sequence framework
│   └── spinechoshaped.py   # Shaped pulse framework
├── gui/                     # GUI applications
├── examples/                # Example scripts and demos
├── docs/                    # Documentation files
└── tests/                   # Test suite
```

### Dependencies

The code uses standard scientific Python libraries:
- `numpy>=1.20.0`: Numerical computations and matrix operations
- `scipy>=1.7.0`: Matrix exponential functions for quantum evolution
- `matplotlib>=3.5.0`: Plotting and visualization
- `joblib>=1.1.0`: Parallel processing optimization
- `tkinter`: GUI interfaces (usually bundled with Python)
- `jupyter`: Interactive notebook environment

## Development Workflow

### Installation and Setup

**Development installation (recommended):**
```bash
pip install -e .                    # Install in development mode
pulseseq-validate                   # Validate installation
```

**With development tools:**
```bash
pip install -e ".[dev]"             # Install with linting/testing tools
pip install -e ".[all]"             # Install everything (GUI, docs, dev tools)
```

### Build, Test, and Lint Commands

**Code formatting and linting:**
```bash
black .                             # Format code with Black
isort .                             # Sort imports
flake8 .                            # Lint code
```

**Testing:**
```bash
pytest                              # Run tests (when test suite exists)
pytest pulseseq/tests/              # Run specific test directory
python test_*.py                    # Run individual test files
```

**Package building:**
```bash
pip install build                   # Install build tools
python -m build                     # Build wheel and source distribution
```

### Command Line Interface

The package provides several CLI commands after installation:

**Quick validation and demos:**
```bash
pulseseq-validate                   # Validate installation
pulseseq-quick-demo                 # Fast demo (~30 seconds)
pulseseq-examples                   # Comprehensive examples (~2-3 minutes)
pulseseq-benchmark                  # Performance benchmark
```

**GUI applications:**
```bash
pulseseq-gui-basic                  # Original GUI interface
pulseseq-gui-shaped                 # Advanced shaped pulse GUI
```

### Legacy Scripts (Direct Python Execution)

**Fast exploration (30 seconds):**
```bash
python quick_examples.py                        # Quick shaped pulse demos
```

**Comprehensive examples (2-3 minutes):**
```bash
python shaped_pulse_examples.py                 # All pulse types comparison
python wurst_demo.py                           # WURST pulse specialization
python pulse_analysis.py                       # Quantitative analysis
```

**GUI applications:**
```bash
python interactive_spin_echo_2p_3p.py          # Original multi-core GUI
python interactive_spin_echo_2p_3p_single_core.py  # Single-core GUI
python tkinter_pulse_gui.py                    # Interactive shaped pulse explorer
```

**Educational resources:**
```bash
jupyter notebook 1.ipynb                       # Comprehensive tutorial
jupyter notebook simple_hahn_echo_notebook.ipynb  # Beginner tutorial
jupyter notebook SHAPED_PULSE_TUTORIAL.md      # Shaped pulse guide
```

**Performance analysis:**
```bash
python Benchmark.py                            # Multi-core performance benchmark
```

### Framework Usage Patterns

**Basic spin echo (original framework):**
```python
# Use interactive_spin_echo_2p_3p.py for traditional sequences
```

**Shaped pulse simulations (new package structure):**
```python
from pulseseq import ShapedPulseSequence, ShapedSpinEchoSimulator
import numpy as np

sequence = (ShapedPulseSequence("Demo")
    .add_shaped_pulse(np.pi/2, 1.0, 'gaussian')
    .add_delay(5.0)
    .add_shaped_pulse(np.pi, 1.0, 'gaussian')
    .set_detection(0.01, 1000))

simulator = ShapedSpinEchoSimulator(n_jobs=4)
signals = simulator.simulate_sequence(sequence, linewidth=2.0)
```

**Flexible sequence design:**
```python
from pulseseq import SequenceBuilder, PulseParameters, DelayParameters
import numpy as np

builder = SequenceBuilder()
sequence = (builder
    .add_pulse(PulseParameters(flip_angle=np.pi/2))
    .add_delay(DelayParameters(duration=5.0))
    .add_pulse(PulseParameters(flip_angle=np.pi))
    .build())
```

**Legacy imports (still work for backward compatibility):**
```python
# Direct imports from core modules
from pulseseq.core.spinechoshaped import ShapedPulseSequence, ShapedSpinEchoSimulator
from pulseseq.core.spinecho import SequenceBuilder, PulseParameters
```

### Dependency Management
This project uses modern Python packaging with pyproject.toml:
```bash
# Basic installation
pip install .                       # Install package only
pip install -e .                    # Development mode

# With optional dependencies
pip install ".[gui]"                # GUI support (tkinter)
pip install ".[notebooks]"          # Jupyter notebook support
pip install ".[dev]"                # Development tools (pytest, black, flake8, isort)
pip install ".[docs]"               # Documentation tools
pip install ".[all]"                # Everything
```

### Testing and Validation

**Testing infrastructure is available** with pytest configuration:

**Formal testing (when test suite exists):**
```bash
pytest                              # Run all tests
pytest pulseseq/tests/              # Run package tests
pytest test_*.py                    # Run legacy test files
```

**Quick validation:**
```bash
pulseseq-validate                   # Package installation validation
python quick_examples.py           # Fast functional tests
```

**Comprehensive validation:**
```bash
pulseseq-examples                   # CLI comprehensive examples
python shaped_pulse_examples.py    # Full feature testing
pulseseq-benchmark                  # Performance validation
```

**Educational validation:**
- Run Jupyter notebook examples (`1.ipynb`, `simple_hahn_echo_notebook.ipynb`)
- Compare simulation outputs with expected NMR/ESR physics
- Visual inspection of echo formation at t ≈ 2τ
- Cross-reference with `SHAPED_PULSE_TUTORIAL.md` expected results

### Code Conventions

- **Naming**: snake_case for functions, PascalCase for classes
- **Documentation**: Extensive docstrings explaining physics parameters
- **Constants**: Pauli matrices (SX, SY, SZ) as global constants
- **Complex numbers**: Used for quantum state representation
- **Parallel processing**: joblib.Parallel with n_jobs parameter control
- **GUI frameworks**: tkinter with matplotlib integration
- **Sequence patterns**: Method chaining with builder pattern for `spinechoshaped.py`

### Framework Selection Guide

**Use `interactive_spin_echo_2p_3p.py` when:**
- Teaching basic 2-pulse/3-pulse echo sequences
- Working with traditional hard/soft pulses
- Need simple GUI for parameter exploration

**Use `spinechoshaped.py` when:**
- Exploring advanced pulse shapes (WURST, SECH, chirped)
- Need multi-axis (Sx/Sy) control
- Building complex shaped pulse sequences
- Require high-precision time-sliced evolution

**Use `spinecho.py` when:**
- Designing arbitrary pulse sequences
- Need object-oriented extensibility
- Building custom sequence types
- Want clean separation of pulse parameters

### Common Development Tasks

**Adding new pulse shapes to `spinechoshaped.py`:**
1. Implement shape function in `PulseShapeGenerator.create_pulse_shape()`
2. Add shape parameters to the method's conditional logic
3. Test with `quick_examples.py` framework
4. Update `SHAPED_PULSE_TUTORIAL.md` documentation

**Creating custom sequences:**
```python
# For shaped pulses
sequence = (ShapedPulseSequence("Custom")
    .add_shaped_pulse(flip_angle, duration, shape_type, shape_params)
    .add_delay(delay_time)
    .set_detection(time_step, num_points))

# For flexible sequences
sequence = (PulseSequenceBuilder()
    .add_pulse(PulseParameters(...))
    .add_delay(DelayParameters(...))
    .build())
```

**Performance optimization:**
- Use `n_jobs=4` for moderate parallelization
- Adjust `detuning_points` (31-101) for accuracy vs speed
- Tune `n_time_slices` (50-100) for shaped pulse precision
- Run `Benchmark.py` to test performance scaling

**GUI customization:**
- Modify `tkinter_pulse_gui.py` for shaped pulse interfaces
- Extend `interactive_spin_echo_2p_3p.py` for traditional sequences
- Add new parameter controls following existing patterns

## Physics Context

**Core Physical Model:**
- **Spin-1/2 systems**: Electron or nuclear spins in magnetic fields
- **Density matrix formalism**: ρ = |ψ⟩⟨ψ| quantum state representation
- **Hamiltonian evolution**: H = ωRF(t)·S + δ·SZ + interactions

**Key Parameters:**
- **Detuning (δ)**: Frequency offset from resonance (typically ±10 units)
- **Flip angles**: θₓ, θᵧ for rotations (π/2 ≈ 1.57, π ≈ 3.14 radians)
- **Echo delays**: τ, τ₁, τ₂ timing parameters (typically 1-10 time units)
- **Pulse duration**: Physical length of RF pulses (shaped: 1-3 units, hard: instantaneous)
- **Line broadening**: Inhomogeneous distributions (Gaussian σ ~ 1-3 units)

**Advanced Concepts:**
- **Multi-axis evolution**: Sx and Sy components with independent amplitudes
- **Frequency sweeps**: WURST (±10 units), chirped pulses for broadband excitation
- **Adiabatic passage**: SECH pulses for robust, slow transitions
- **Composite pulses**: Multiple pulse sequences for enhanced performance
- **Phase cycling**: Systematic phase variations for artifact suppression

**Expected Results:**
- **Echo formation**: Signal peaks at t ≈ 2τ for 2-pulse sequences
- **WURST efficiency**: Lower amplitude but broader bandwidth than Gaussian
- **Multi-axis effects**: Modified Sx/Sy ratios while conserving total signal power
- **Noise degradation**: 10-40% signal reduction with realistic experimental noise
