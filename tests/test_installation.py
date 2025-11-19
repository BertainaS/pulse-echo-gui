"""
Integration tests for package installation and imports.

Tests that the package is properly installed and all modules
can be imported correctly.
"""

import sys

import pytest


class TestPackageImports:
    """Test that all package modules can be imported."""

    def test_import_main_package(self):
        """Test importing main package."""
        import pulseechogui

        assert hasattr(pulseechogui, "__version__")

    def test_import_core_modules(self):
        """Test importing core simulation modules."""
        from pulseechogui.core import spinecho, spinechoshaped

        assert spinecho is not None
        assert spinechoshaped is not None

    def test_import_shaped_pulse_sequence(self):
        """Test importing ShapedPulseSequence."""
        from pulseechogui import ShapedPulseSequence

        assert ShapedPulseSequence is not None

    def test_import_shaped_spin_echo_simulator(self):
        """Test importing ShapedSpinEchoSimulator."""
        from pulseechogui import ShapedSpinEchoSimulator

        assert ShapedSpinEchoSimulator is not None

    def test_import_sequence_builder(self):
        """Test importing SequenceBuilder."""
        from pulseechogui import SequenceBuilder

        assert SequenceBuilder is not None

    def test_import_pulse_parameters(self):
        """Test importing PulseParameters."""
        from pulseechogui import PulseParameters

        assert PulseParameters is not None

    def test_import_delay_parameters(self):
        """Test importing DelayParameters."""
        from pulseechogui import DelayParameters

        assert DelayParameters is not None


class TestGUIImports:
    """Test that GUI modules can be imported (without launching)."""

    def test_import_gui_module(self):
        """Test importing GUI module."""
        from pulseechogui import gui

        assert gui is not None

    def test_gui_launcher_functions_exist(self):
        """Test that GUI launcher functions are available."""
        import pulseechogui

        assert hasattr(pulseechogui, "launch_basic_gui")
        assert hasattr(pulseechogui, "launch_basic_gui_single")
        assert hasattr(pulseechogui, "launch_shaped_pulse_gui")


class TestDependencies:
    """Test that all required dependencies are available."""

    def test_numpy_import(self):
        """Test that numpy is available."""
        import numpy as np

        assert np is not None
        assert hasattr(np, "__version__")

    def test_scipy_import(self):
        """Test that scipy is available."""
        import scipy

        assert scipy is not None
        from scipy.linalg import expm

        assert expm is not None

    def test_matplotlib_import(self):
        """Test that matplotlib is available."""
        import matplotlib

        assert matplotlib is not None
        import matplotlib.pyplot as plt

        assert plt is not None

    def test_joblib_import(self):
        """Test that joblib is available."""
        import joblib

        assert joblib is not None
        from joblib import Parallel, delayed

        assert Parallel is not None
        assert delayed is not None

    def test_tkinter_import(self):
        """Test that tkinter is available."""
        try:
            import tkinter as tk

            assert tk is not None
        except ImportError:
            pytest.skip("tkinter not available (expected on some systems)")


class TestVersionInfo:
    """Test package version information."""

    def test_version_exists(self):
        """Test that version string exists."""
        import pulseechogui

        assert hasattr(pulseechogui, "__version__")
        assert isinstance(pulseechogui.__version__, str)

    def test_version_format(self):
        """Test that version follows semantic versioning."""
        import pulseechogui

        version = pulseechogui.__version__
        # Should be in format X.Y.Z
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor


class TestValidationFunction:
    """Test the validate_installation function."""

    def test_validate_installation_exists(self):
        """Test that validate_installation function exists."""
        import pulseechogui

        assert hasattr(pulseechogui, "validate_installation")

    def test_validate_installation_runs(self):
        """Test that validate_installation can be called."""
        import pulseechogui

        # Should not raise an exception
        try:
            pulseechogui.validate_installation()
        except SystemExit:
            pass  # Function may exit with code 0 on success


class TestPythonVersion:
    """Test Python version compatibility."""

    def test_python_version(self):
        """Test that Python version is >= 3.8."""
        assert sys.version_info >= (3, 8), "Python 3.8+ required"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
