"""
Core simulation modules for PulseEchoGui.

This module provides the fundamental quantum mechanics simulation
capabilities for NMR/ESR pulse sequences.
"""

from .spinecho import (
    DelayParameters,
    DetectionParameters,
    PulseParameters,
    PulseSequence,
    QuantumEvolution,
    SequenceBuilder,
    SpinEchoSimulator,
)
from .spinechoshaped import (
    PulseShapeFactory,
    ShapedPulseSequence,
    ShapedSpinEchoSimulator,
    plot_pulse_shape,
)

__all__ = [
    # spinecho exports
    "SequenceBuilder",
    "PulseParameters",
    "DelayParameters",
    "DetectionParameters",
    "QuantumEvolution",
    "PulseSequence",
    "SpinEchoSimulator",
    # spinechoshaped exports
    "ShapedPulseSequence",
    "ShapedSpinEchoSimulator",
    "PulseShapeFactory",
    "plot_pulse_shape",
]
