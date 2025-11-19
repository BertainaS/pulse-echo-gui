"""
Pytest configuration and shared fixtures for PulseEchoGui tests.
"""

import numpy as np
import pytest

# Pauli matrices (same convention as code)
SX = 0.5 * np.array([[0, 1], [1, 0]], dtype=complex)
SY = 0.5 * np.array([[0, -1j], [1j, 0]], dtype=complex)
SZ = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
RHO_EQ = 0.5 * np.array([[1, 0], [0, 1]], dtype=complex) + SZ


@pytest.fixture
def pauli_matrices():
    """Provide Pauli matrices for tests."""
    return {"sx": SX, "sy": SY, "sz": SZ}


@pytest.fixture
def equilibrium_state():
    """Provide thermal equilibrium density matrix."""
    return RHO_EQ.copy()


@pytest.fixture
def identity_matrix():
    """Provide 2x2 identity matrix."""
    return np.eye(2, dtype=complex)


@pytest.fixture
def typical_parameters():
    """Provide typical simulation parameters."""
    return {
        "flip_angle": np.pi / 2,
        "phase": 0.0,
        "echo_delay": 5.0,
        "detuning": 2.0,
        "linewidth": 2.0,
        "pulse_duration": 1.0,
        "detuning_points": 31,
        "time_step": 0.01,
        "detection_points": 1000,
    }


@pytest.fixture
def tolerance():
    """Provide numerical tolerance for comparisons."""
    return {
        "atol": 1e-10,  # Absolute tolerance
        "rtol": 1e-8,  # Relative tolerance
    }


def validate_density_matrix(rho, tol=1e-10):
    """
    Validate that a matrix is a proper density matrix.

    Parameters
    ----------
    rho : np.ndarray
        Matrix to validate
    tol : float
        Numerical tolerance

    Returns
    -------
    bool
        True if valid, raises AssertionError otherwise
    """
    # Check hermiticity
    assert np.allclose(rho, rho.conj().T, atol=tol), "Density matrix not Hermitian"

    # Check trace = 1
    trace = np.trace(rho)
    assert np.isclose(trace, 1.0, atol=tol), f"Trace = {trace}, expected 1.0"

    # Check positive semidefinite
    eigenvalues = np.linalg.eigvalsh(rho.real)
    assert np.all(eigenvalues >= -tol), f"Negative eigenvalues: {eigenvalues}"

    return True


def validate_unitary(U, tol=1e-10):
    """
    Validate that a matrix is unitary (U†U = I).

    Parameters
    ----------
    U : np.ndarray
        Matrix to validate
    tol : float
        Numerical tolerance

    Returns
    -------
    bool
        True if unitary, raises AssertionError otherwise
    """
    identity = np.eye(U.shape[0], dtype=complex)
    product = U @ U.conj().T
    assert np.allclose(product, identity, atol=tol), "Matrix is not unitary"
    return True


@pytest.fixture
def validation_functions():
    """Provide validation helper functions."""
    return {
        "density_matrix": validate_density_matrix,
        "unitary": validate_unitary,
    }
