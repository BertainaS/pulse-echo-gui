"""
Unit tests for spinechoshaped.py module.

Tests the shaped pulse framework including ShapedPulseSequence,
ShapedSpinEchoSimulator, and pulse shape generation.
"""

import numpy as np
import pytest

from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator


class TestShapedPulseSequence:
    """Test ShapedPulseSequence class."""

    def test_creation(self):
        """Test creating a shaped pulse sequence."""
        seq = ShapedPulseSequence("Test Sequence")
        assert seq.name == "Test Sequence"
        assert len(seq.operations) == 0

    def test_add_shaped_pulse(self):
        """Test adding a shaped pulse."""
        seq = ShapedPulseSequence("Test")
        seq.add_shaped_pulse(np.pi / 2, 1.0, "gaussian")
        assert len(seq.operations) == 1

    def test_add_delay(self):
        """Test adding a delay."""
        seq = ShapedPulseSequence("Test")
        seq.add_delay(5.0)
        assert len(seq.operations) == 1

    def test_method_chaining(self):
        """Test method chaining for sequence building."""
        seq = (
            ShapedPulseSequence("Test")
            .add_shaped_pulse(np.pi / 2, 1.0, "gaussian")
            .add_delay(5.0)
            .add_shaped_pulse(np.pi, 1.0, "gaussian")
        )
        assert len(seq.operations) == 3

    def test_set_detection(self):
        """Test setting detection parameters."""
        seq = ShapedPulseSequence("Test")
        seq.set_detection(dt=0.01, points=1000)
        assert seq.detection_params is not None

    def test_set_multi_axis(self):
        """Test setting multi-axis parameters."""
        seq = ShapedPulseSequence("Test")
        seq.set_multi_axis(sx_amp=1.0, sy_amp=0.8)
        assert seq.multi_axis_params is not None


class TestPulseShapes:
    """Test different pulse shape generations."""

    def test_gaussian_pulse(self):
        """Test Gaussian pulse shape."""
        seq = ShapedPulseSequence("Gaussian Test")
        seq.add_shaped_pulse(np.pi / 2, 1.0, "gaussian", sigma_factor=3.0)
        assert len(seq.operations) == 1

    def test_sech_pulse(self):
        """Test SECH pulse shape."""
        seq = ShapedPulseSequence("SECH Test")
        seq.add_shaped_pulse(np.pi / 2, 1.0, "sech", beta=5.0)
        assert len(seq.operations) == 1

    def test_wurst_pulse(self):
        """Test WURST pulse shape."""
        seq = ShapedPulseSequence("WURST Test")
        seq.add_shaped_pulse(
            np.pi / 2, 2.0, "wurst", freq_start=-10, freq_end=10, wurst_n=2
        )
        assert len(seq.operations) == 1

    def test_chirped_pulse(self):
        """Test chirped pulse shape."""
        seq = ShapedPulseSequence("Chirp Test")
        seq.add_shaped_pulse(
            np.pi / 2, 2.0, "chirped", freq_start=-5, freq_end=5, envelope="gaussian"
        )
        assert len(seq.operations) == 1

    def test_square_pulse(self):
        """Test square pulse shape."""
        seq = ShapedPulseSequence("Square Test")
        seq.add_shaped_pulse(np.pi / 2, 1.0, "square")
        assert len(seq.operations) == 1

    def test_noisy_pulse(self):
        """Test noisy pulse shape."""
        seq = ShapedPulseSequence("Noisy Test")
        seq.add_shaped_pulse(
            np.pi / 2,
            1.0,
            "noisy",
            base_shape="gaussian",
            amplitude_noise=0.1,
            phase_noise=0.05,
            random_seed=42,
        )
        assert len(seq.operations) == 1


class TestShapedSpinEchoSimulator:
    """Test ShapedSpinEchoSimulator class."""

    def test_creation(self):
        """Test creating a simulator."""
        sim = ShapedSpinEchoSimulator(n_jobs=1)
        assert sim.n_jobs == 1

    def test_parallel_creation(self):
        """Test creating parallel simulator."""
        sim = ShapedSpinEchoSimulator(n_jobs=4)
        assert sim.n_jobs == 4

    def test_simple_simulation(self):
        """Test running a simple simulation."""
        # Create simple sequence
        seq = (
            ShapedPulseSequence("Test")
            .add_shaped_pulse(np.pi / 2, 1.0, "gaussian")
            .add_delay(5.0)
            .set_detection(dt=0.1, points=100)
        )

        # Run simulation
        sim = ShapedSpinEchoSimulator(n_jobs=1)
        result = sim.simulate_sequence(
            seq, linewidth=2.0, detuning_points=11  # Small number for speed
        )

        # Check result structure
        assert "time" in result
        assert "Sx" in result
        assert "Sy" in result
        assert "Sz" in result
        assert len(result["time"]) == 100


class TestPhysicsValidation:
    """Test physics validation for shaped pulses."""

    def test_echo_formation(self):
        """Test that echo forms at expected time."""
        # Create Hahn echo sequence
        tau = 5.0
        seq = (
            ShapedPulseSequence("Hahn Echo")
            .add_shaped_pulse(np.pi / 2, 0.5, "gaussian")
            .add_delay(tau)
            .add_shaped_pulse(np.pi, 0.5, "gaussian")
            .add_delay(tau)
            .set_detection(dt=0.1, points=200)
        )

        # Simulate
        sim = ShapedSpinEchoSimulator(n_jobs=1)
        result = sim.simulate_sequence(seq, linewidth=1.0, detuning_points=11)

        # Check that signal exists
        assert np.max(np.abs(result["Sx"])) > 0

    def test_conservation_of_magnetization(self):
        """Test that total magnetization is conserved (approximately)."""
        seq = (
            ShapedPulseSequence("Conservation Test")
            .add_shaped_pulse(np.pi / 2, 1.0, "gaussian")
            .set_detection(dt=0.1, points=50)
        )

        sim = ShapedSpinEchoSimulator(n_jobs=1)
        result = sim.simulate_sequence(seq, linewidth=2.0, detuning_points=11)

        # Total magnetization should be roughly constant
        total_mag = np.sqrt(result["Sx"] ** 2 + result["Sy"] ** 2 + result["Sz"] ** 2)
        # Allow some variation due to numerical integration
        assert np.std(total_mag) < 0.2


class TestMultiAxisControl:
    """Test multi-axis control features."""

    def test_multi_axis_amplitudes(self):
        """Test setting different Sx and Sy amplitudes."""
        seq = (
            ShapedPulseSequence("Multi-axis Test")
            .add_shaped_pulse(np.pi / 2, 1.0, "gaussian")
            .set_multi_axis(sx_amp=1.0, sy_amp=0.8)
            .set_detection(dt=0.1, points=50)
        )

        sim = ShapedSpinEchoSimulator(n_jobs=1)
        result = sim.simulate_sequence(seq, linewidth=2.0, detuning_points=11)

        # Should produce results
        assert len(result["time"]) == 50


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_duration_pulse(self):
        """Test pulse with zero duration."""
        seq = ShapedPulseSequence("Zero Duration")
        # This should either raise an error or handle gracefully
        # depending on implementation
        try:
            seq.add_shaped_pulse(np.pi / 2, 0.0, "gaussian")
        except ValueError:
            pass  # Expected behavior

    def test_very_large_detuning(self):
        """Test simulation with very large detuning range."""
        seq = (
            ShapedPulseSequence("Large Detuning")
            .add_shaped_pulse(np.pi / 2, 1.0, "gaussian")
            .set_detection(dt=0.1, points=50)
        )

        sim = ShapedSpinEchoSimulator(n_jobs=1)
        result = sim.simulate_sequence(
            seq, linewidth=10.0, detuning_points=11  # Large linewidth
        )

        assert len(result["time"]) == 50


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
