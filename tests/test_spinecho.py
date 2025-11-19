"""
Unit tests for spinecho.py module.

Tests the flexible sequence framework including SequenceBuilder,
PulseParameters, and SpinEchoSimulator.
"""

import pytest
import numpy as np
from pulseechogui import SequenceBuilder, PulseParameters, DelayParameters


class TestPulseParameters:
    """Test PulseParameters dataclass."""

    def test_creation_default(self):
        """Test creating PulseParameters with defaults."""
        params = PulseParameters(flip_angle=np.pi / 2)
        assert params.flip_angle == np.pi / 2
        assert params.phase == 0.0
        assert params.duration == 0.0
        assert params.pulse_type == "hard"

    def test_creation_custom(self):
        """Test creating PulseParameters with custom values."""
        params = PulseParameters(
            flip_angle=np.pi,
            phase=np.pi / 2,
            duration=1.0,
            pulse_type="soft",
            amplitude=0.95,
        )
        assert params.flip_angle == np.pi
        assert params.phase == np.pi / 2
        assert params.duration == 1.0
        assert params.pulse_type == "soft"
        assert params.amplitude == 0.95

    def test_invalid_flip_angle(self):
        """Test that invalid flip angles are rejected."""
        with pytest.raises(ValueError):
            PulseParameters(flip_angle=np.nan)

    def test_invalid_amplitude(self):
        """Test that invalid amplitudes are rejected."""
        with pytest.raises(ValueError):
            PulseParameters(flip_angle=np.pi / 2, amplitude=0.0)

        with pytest.raises(ValueError):
            PulseParameters(flip_angle=np.pi / 2, amplitude=-0.5)


class TestDelayParameters:
    """Test DelayParameters dataclass."""

    def test_creation(self):
        """Test creating DelayParameters."""
        params = DelayParameters(duration=5.0)
        assert params.duration == 5.0

    def test_invalid_duration(self):
        """Test that negative durations are rejected."""
        with pytest.raises(ValueError):
            DelayParameters(duration=-1.0)


class TestSequenceBuilder:
    """Test SequenceBuilder class."""

    def test_empty_sequence(self):
        """Test building an empty sequence."""
        builder = SequenceBuilder()
        sequence = builder.build()
        assert len(sequence) == 0

    def test_single_pulse(self):
        """Test sequence with single pulse."""
        builder = SequenceBuilder()
        sequence = builder.add_pulse(PulseParameters(flip_angle=np.pi / 2)).build()
        assert len(sequence) == 1
        assert sequence[0].flip_angle == np.pi / 2

    def test_pulse_and_delay(self):
        """Test sequence with pulse and delay."""
        builder = SequenceBuilder()
        sequence = (
            builder.add_pulse(PulseParameters(flip_angle=np.pi / 2))
            .add_delay(DelayParameters(duration=5.0))
            .build()
        )
        assert len(sequence) == 2

    def test_hahn_echo_sequence(self):
        """Test building a Hahn echo sequence."""
        builder = SequenceBuilder()
        sequence = (
            builder.add_pulse(PulseParameters(flip_angle=np.pi / 2))
            .add_delay(DelayParameters(duration=5.0))
            .add_pulse(PulseParameters(flip_angle=np.pi))
            .add_delay(DelayParameters(duration=5.0))
            .build()
        )
        assert len(sequence) == 4
        assert sequence[0].flip_angle == np.pi / 2
        assert sequence[2].flip_angle == np.pi

    def test_method_chaining(self):
        """Test that builder methods return self for chaining."""
        builder = SequenceBuilder()
        result = builder.add_pulse(PulseParameters(flip_angle=np.pi / 2))
        assert isinstance(result, SequenceBuilder)


class TestPhysicsValidation:
    """Test physics validation functions."""

    def test_density_matrix_validation(
        self, equilibrium_state, validation_functions
    ):
        """Test that equilibrium state is valid density matrix."""
        validate = validation_functions["density_matrix"]
        assert validate(equilibrium_state)

    def test_invalid_density_matrix(self, validation_functions):
        """Test that invalid matrices are rejected."""
        validate = validation_functions["density_matrix"]

        # Non-Hermitian matrix
        invalid = np.array([[1, 1j], [0, 0]], dtype=complex)
        with pytest.raises(AssertionError):
            validate(invalid)

        # Wrong trace
        invalid = np.array([[0.5, 0], [0, 0.5]], dtype=complex)
        with pytest.raises(AssertionError):
            validate(invalid)

    def test_pauli_commutators(self, pauli_matrices):
        """Test Pauli matrix commutation relations."""
        sx = pauli_matrices["sx"]
        sy = pauli_matrices["sy"]
        sz = pauli_matrices["sz"]

        # [Sx, Sy] = i·Sz
        commutator = sx @ sy - sy @ sx
        expected = 1j * sz
        np.testing.assert_allclose(commutator, expected, atol=1e-10)

        # [Sy, Sz] = i·Sx
        commutator = sy @ sz - sz @ sy
        expected = 1j * sx
        np.testing.assert_allclose(commutator, expected, atol=1e-10)

        # [Sz, Sx] = i·Sy
        commutator = sz @ sx - sx @ sz
        expected = 1j * sy
        np.testing.assert_allclose(commutator, expected, atol=1e-10)


class TestNumericalAccuracy:
    """Test numerical accuracy and edge cases."""

    def test_zero_flip_angle(self):
        """Test evolution with zero flip angle (identity)."""
        params = PulseParameters(flip_angle=0.0)
        assert params.flip_angle == 0.0

    def test_small_flip_angle(self):
        """Test evolution with very small flip angle."""
        params = PulseParameters(flip_angle=1e-12)
        assert abs(params.flip_angle) < 1e-10

    def test_large_flip_angle(self):
        """Test evolution with large flip angles."""
        params = PulseParameters(flip_angle=10 * np.pi)
        assert params.flip_angle > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
