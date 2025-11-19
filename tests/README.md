# PulseEchoGui Tests

This directory contains the test suite for PulseEchoGui.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── conftest.py                 # Pytest configuration and fixtures
├── test_installation.py        # Package installation and import tests
├── test_spinecho.py           # Tests for spinecho.py module
├── test_spinechoshaped.py     # Tests for spinechoshaped.py module
└── README.md                   # This file
```

## Running Tests

### Run All Tests

```bash
# From project root
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=pulseechogui --cov-report=html
```

### Run Specific Test Files

```bash
# Test installation and imports
pytest tests/test_installation.py -v

# Test spinecho module
pytest tests/test_spinecho.py -v

# Test spinechoshaped module
pytest tests/test_spinechoshaped.py -v
```

### Run Specific Test Classes or Functions

```bash
# Run specific test class
pytest tests/test_spinecho.py::TestPulseParameters -v

# Run specific test function
pytest tests/test_spinecho.py::TestPulseParameters::test_creation_default -v
```

## Test Categories

### Installation Tests (`test_installation.py`)
- Package imports
- Dependency availability
- Version information
- GUI module imports (without launching)
- Python version compatibility

### Core Module Tests (`test_spinecho.py`)
- PulseParameters dataclass
- DelayParameters dataclass
- SequenceBuilder functionality
- Method chaining
- Physics validation (Pauli matrices, commutators)
- Numerical accuracy

### Shaped Pulse Tests (`test_spinechoshaped.py`)
- ShapedPulseSequence creation
- Pulse shape generation (Gaussian, SECH, WURST, chirped, noisy)
- ShapedSpinEchoSimulator
- Echo formation validation
- Multi-axis control
- Conservation laws
- Edge cases

## Fixtures

Common fixtures are defined in `conftest.py`:

- `pauli_matrices`: Pauli matrices (Sx, Sy, Sz)
- `equilibrium_state`: Thermal equilibrium density matrix
- `identity_matrix`: 2×2 identity matrix
- `typical_parameters`: Standard simulation parameters
- `tolerance`: Numerical tolerances for comparisons
- `validation_functions`: Helper functions for physics validation

## Writing New Tests

### Test File Template

```python
"""
Description of what is being tested.
"""

import pytest
import numpy as np
from pulseechogui import YourModule


class TestYourFeature:
    """Test YourFeature class or function."""

    def test_basic_functionality(self):
        """Test basic usage."""
        # Arrange
        input_data = setup_test_data()

        # Act
        result = your_function(input_data)

        # Assert
        assert result.expected_property == expected_value
        np.testing.assert_allclose(result.array, expected_array)

    def test_edge_case(self):
        """Test edge case behavior."""
        with pytest.raises(ValueError):
            your_function(invalid_input)
```

### Using Fixtures

```python
def test_with_fixtures(pauli_matrices, equilibrium_state):
    """Test using predefined fixtures."""
    sx = pauli_matrices["sx"]
    rho = equilibrium_state
    # Your test code
```

### Physics Validation

For quantum mechanical tests, use validation helpers:

```python
def test_unitarity(validation_functions):
    """Test that operator is unitary."""
    U = compute_evolution_operator()
    validate = validation_functions["unitary"]
    assert validate(U)
```

## Test Coverage Goals

- **Unit tests**: Test individual functions and classes
- **Integration tests**: Test complete workflows
- **Physics validation**: Verify quantum mechanical correctness
- **Edge cases**: Test boundary conditions and error handling

### Target Coverage

- Core modules (`spinecho.py`, `spinechoshaped.py`): > 80%
- Public API: > 90%
- GUI modules: Basic import tests (full GUI testing requires X server)

## Continuous Integration

Tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run tests
  run: |
    pip install -e ".[dev]"
    pytest --cov=pulseechogui --cov-report=xml
```

## Performance Tests

For performance-sensitive code:

```python
def test_simulation_performance(benchmark):
    """Benchmark simulation speed."""
    seq = create_test_sequence()
    sim = ShapedSpinEchoSimulator(n_jobs=1)

    result = benchmark(sim.simulate_sequence, seq, linewidth=2.0)
```

Install pytest-benchmark: `pip install pytest-benchmark`

## Troubleshooting

### Tests Failing

1. **Import errors**: Ensure package is installed (`pip install -e .`)
2. **Missing dependencies**: Install dev dependencies (`pip install -e ".[dev]"`)
3. **Numerical precision**: Adjust tolerances in `conftest.py`

### Tkinter Tests

GUI tests may fail on headless systems (no X server):

```bash
# Skip GUI tests
pytest -m "not gui"

# Or install virtual display (Linux)
sudo apt-get install xvfb
xvfb-run pytest
```

### Parallel Test Execution

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Contributing Tests

When contributing new features:

1. **Add tests** for all new functionality
2. **Update fixtures** if adding new common patterns
3. **Document tests** with clear docstrings
4. **Validate physics** for quantum mechanical code
5. **Check coverage**: `pytest --cov=pulseechogui`

See [CONTRIBUTING.md](../CONTRIBUTING.md) for more details.

## Questions

For questions about tests:
- Check existing test files for examples
- See [pytest documentation](https://docs.pytest.org/)
- Contact: sylvain.bertaina@cnrs.fr

---

**Last updated**: November 2, 2024
