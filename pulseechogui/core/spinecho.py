#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Refactored Spin Echo Simulation with User-Defined Sequences

This module provides a flexible framework for creating and simulating
arbitrary pulse sequences in NMR/ESR experiments.

@author: sylvainbertaina
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
from joblib import Parallel, delayed
from scipy.linalg import expm

# Pauli matrices (global constants)
SZ = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
SX = 0.5 * np.array([[0, 1], [1, 0]], dtype=complex)
SY = 0.5 * np.array([[0, 1j], [-1j, 0]], dtype=complex)


@dataclass
class PulseParameters:
    """Parameters for a pulse operation"""

    flip_angle: float  # radians
    phase: float = 0.0  # radians
    amplitude: float = 1.0  # relative amplitude (h1 scaling)
    pulse_type: str = "hard"  # "hard" or "soft"
    duration: Optional[float] = None  # for soft pulses


@dataclass
class DelayParameters:
    """Parameters for a delay/evolution operation"""

    duration: float  # time units


@dataclass
class DetectionParameters:
    """Parameters for signal detection"""

    time_step: float
    num_points: int
    observables: List[str] = field(default_factory=lambda: ["sx", "sy"])


class QuantumEvolution:
    """Handles quantum mechanical evolution operations"""

    @staticmethod
    def evolution_operator(
        theta_x: float, theta_z: float, phase: float = 0.0
    ) -> np.ndarray:
        """Create evolution operator U = exp(-i(theta_x*sigma_x + theta_z*sigma_z))"""
        if abs(theta_x) > 1e-12:
            cos_half = np.cos(theta_x / 2)
            sin_half = np.sin(theta_x / 2)
            if abs(phase) > 1e-12:
                pulse_op = np.cos(phase) * SX + np.sin(phase) * SY
            else:
                pulse_op = SX
            Ux = cos_half * np.eye(2, dtype=complex) - 1j * sin_half * pulse_op
        else:
            Ux = np.eye(2, dtype=complex)

        if abs(theta_z) > 1e-12:
            Uz = expm(-1j * theta_z * SZ)
        else:
            Uz = np.eye(2, dtype=complex)

        return Uz @ Ux

    @staticmethod
    def apply_pulse(
        rho: np.ndarray, params: PulseParameters, delta: float
    ) -> np.ndarray:
        """Apply a pulse to the density matrix"""
        theta_x = params.flip_angle * params.amplitude

        if params.pulse_type == "hard":
            U = QuantumEvolution.evolution_operator(theta_x, 0, params.phase)
            return U.conj().T @ rho @ U
        else:  # soft pulse
            if params.duration is None:
                raise ValueError("Soft pulse requires duration parameter")

            theta_z = delta * params.duration
            if abs(params.phase) > 1e-12:
                pulse_op = np.cos(params.phase) * SX + np.sin(params.phase) * SY
            else:
                pulse_op = SX

            H_total = (theta_x / params.duration) * pulse_op + delta * SZ
            U_soft = expm(-1j * H_total * params.duration)
            return U_soft.conj().T @ rho @ U_soft

    @staticmethod
    def apply_delay(
        rho: np.ndarray, params: DelayParameters, delta: float
    ) -> np.ndarray:
        """Apply free evolution delay"""
        U_delay = QuantumEvolution.evolution_operator(0, delta * params.duration, 0)
        return U_delay.conj().T @ rho @ U_delay

    @staticmethod
    def measure_observables(
        rho: np.ndarray, observables: List[str]
    ) -> Dict[str, float]:
        """Measure specified observables on the density matrix"""
        measurements = {}
        for obs in observables:
            if obs == "sx":
                measurements[obs] = np.real(np.trace(rho @ SX))
            elif obs == "sy":
                measurements[obs] = np.real(np.trace(rho @ SY))
            elif obs == "sz":
                measurements[obs] = np.real(np.trace(rho @ SZ))
            elif obs == "s+":
                measurements[obs] = np.trace(rho @ (SX + 1j * SY))
            elif obs == "s-":
                measurements[obs] = np.trace(rho @ (SX - 1j * SY))
            else:
                raise ValueError(f"Unknown observable: {obs}")
        return measurements


class SequenceOperation(ABC):
    """Abstract base class for sequence operations"""

    @abstractmethod
    def execute(self, rho: np.ndarray, delta: float) -> np.ndarray:
        """Execute the operation on the density matrix"""
        pass


class PulseOperation(SequenceOperation):
    """Pulse operation in a sequence"""

    def __init__(self, params: PulseParameters):
        self.params = params

    def execute(self, rho: np.ndarray, delta: float) -> np.ndarray:
        return QuantumEvolution.apply_pulse(rho, self.params, delta)


class DelayOperation(SequenceOperation):
    """Delay operation in a sequence"""

    def __init__(self, params: DelayParameters):
        self.params = params

    def execute(self, rho: np.ndarray, delta: float) -> np.ndarray:
        return QuantumEvolution.apply_delay(rho, self.params, delta)


class PulseSequence:
    """Represents a complete pulse sequence"""

    def __init__(self, name: str = "Custom Sequence"):
        self.name = name
        self.operations: List[SequenceOperation] = []
        self.detection_params: Optional[DetectionParameters] = None

    def add_pulse(
        self,
        flip_angle: float,
        phase: float = 0.0,
        amplitude: float = 1.0,
        pulse_type: str = "hard",
        duration: Optional[float] = None,
    ) -> "PulseSequence":
        """Add a pulse to the sequence (fluent interface)"""
        params = PulseParameters(flip_angle, phase, amplitude, pulse_type, duration)
        self.operations.append(PulseOperation(params))
        return self

    def add_delay(self, duration: float) -> "PulseSequence":
        """Add a delay to the sequence (fluent interface)"""
        params = DelayParameters(duration)
        self.operations.append(DelayOperation(params))
        return self

    def set_detection(
        self, time_step: float, num_points: int, observables: List[str] = None
    ) -> "PulseSequence":
        """Set detection parameters"""
        if observables is None:
            observables = ["sx", "sy"]
        self.detection_params = DetectionParameters(time_step, num_points, observables)
        return self

    def simulate(
        self, delta: float, initial_state: Optional[np.ndarray] = None
    ) -> Dict[str, np.ndarray]:
        """Simulate the complete sequence for a given detuning"""
        if self.detection_params is None:
            raise ValueError("Detection parameters must be set before simulation")

        # Initialize density matrix
        if initial_state is None:
            rho = SZ.copy()  # Thermal equilibrium
        else:
            rho = initial_state.copy()

        # Execute sequence operations
        for operation in self.operations:
            rho = operation.execute(rho, delta)

        # Detection with time evolution
        dt = self.detection_params.time_step
        points = self.detection_params.num_points
        observables = self.detection_params.observables

        signals = {
            obs: np.zeros(points, dtype=complex if obs in ["s+", "s-"] else float)
            for obs in observables
        }

        U_evolution = QuantumEvolution.evolution_operator(0, delta * dt, 0)

        for t in range(points):
            measurements = QuantumEvolution.measure_observables(rho, observables)
            for obs in observables:
                signals[obs][t] = measurements[obs]
            rho = U_evolution.conj().T @ rho @ U_evolution

        return signals


class SpinDistribution:
    """Handles spin distribution calculations"""

    @staticmethod
    def calculate_weights(
        delta_values: np.ndarray, linewidth: float, distribution_type: str = "gaussian"
    ) -> np.ndarray:
        """Calculate distribution weights for given detuning values"""
        if distribution_type == "gaussian":
            return np.exp(-((delta_values / linewidth) ** 2))
        elif distribution_type == "lorentzian":
            return 1.0 / (1.0 + (delta_values / linewidth) ** 2)
        elif distribution_type == "exponential":
            return np.exp(-np.abs(delta_values) / linewidth)
        elif distribution_type == "uniform":
            return np.where(np.abs(delta_values) <= linewidth, 1.0, 0.0)
        else:
            raise ValueError(f"Unknown distribution type: {distribution_type}")


class SpinEchoSimulator:
    """Main simulator class for spin echo experiments"""

    def __init__(self, n_jobs: int = -1):
        self.n_jobs = n_jobs

    def simulate_sequence(
        self,
        sequence: PulseSequence,
        detuning_range: Tuple[float, float] = (-10.0, 10.0),
        detuning_points: int = 101,
        linewidth: float = 2.0,
        distribution_type: str = "gaussian",
    ) -> Dict[str, np.ndarray]:
        """Simulate a pulse sequence over a range of detuning values"""

        # Generate detuning values and weights
        delta_values = np.linspace(
            detuning_range[0], detuning_range[1], detuning_points
        )
        weights = SpinDistribution.calculate_weights(
            delta_values, linewidth, distribution_type
        )
        weights = weights / np.sum(weights)  # Normalize

        # Parallel simulation over detuning values
        def simulate_single_detuning(delta):
            return sequence.simulate(delta)

        results_list = Parallel(n_jobs=self.n_jobs, verbose=1)(
            delayed(simulate_single_detuning)(delta) for delta in delta_values
        )

        # Aggregate results with distribution weighting
        observables = sequence.detection_params.observables
        time_points = sequence.detection_params.num_points

        final_signals = {}
        for obs in observables:
            # Stack all signals for this observable
            signals_array = np.array(
                [result[obs] for result in results_list]
            )  # (detuning_points, time_points)
            # Apply weights and sum over detuning values
            weighted_signals = signals_array.T * weights  # Broadcasting
            final_signals[obs] = np.sum(weighted_signals, axis=1)

        return final_signals


# Predefined sequence builders
class SequenceBuilder:
    """Factory class for common pulse sequences"""

    @staticmethod
    def hahn_echo(
        tau: float,
        dt: float = 0.01,
        points: int = 800,
        h1: float = 1.0,
        phase_90: float = 0.0,
        phase_180: float = 0.0,
        pulse_type: str = "hard",
    ) -> PulseSequence:
        """Build a 2-pulse Hahn echo: �/2 - � - � - detection"""
        sequence = PulseSequence("Hahn Echo")
        sequence.add_pulse(np.pi / 2 * h1, phase_90, pulse_type=pulse_type)
        sequence.add_delay(tau)
        sequence.add_pulse(np.pi * h1, phase_180, pulse_type=pulse_type)
        sequence.set_detection(dt, points)
        return sequence

    @staticmethod
    def stimulated_echo(
        tau1: float,
        tau2: float,
        dt: float = 0.01,
        points: int = 800,
        h1: float = 1.0,
        phases: Tuple[float, float, float] = (0.0, np.pi / 2, 0.0),
        pulse_type: str = "hard",
    ) -> PulseSequence:
        """Build a 3-pulse stimulated echo: �/2 - �1 - �/2 - �2 - �/2 - detection"""
        sequence = PulseSequence("Stimulated Echo")
        sequence.add_pulse(np.pi / 2 * h1, phases[0], pulse_type=pulse_type)
        sequence.add_delay(tau1)
        sequence.add_pulse(np.pi / 2 * h1, phases[1], pulse_type=pulse_type)
        sequence.add_delay(tau2)
        sequence.add_pulse(np.pi / 2 * h1, phases[2], pulse_type=pulse_type)
        sequence.set_detection(dt, points)
        return sequence

    @staticmethod
    def inversion_recovery(
        tau: float,
        dt: float = 0.01,
        points: int = 800,
        h1: float = 1.0,
        pulse_type: str = "hard",
    ) -> PulseSequence:
        """Build inversion recovery: � - � - �/2 - detection"""
        sequence = PulseSequence("Inversion Recovery")
        sequence.add_pulse(np.pi * h1, 0.0, pulse_type=pulse_type)
        sequence.add_delay(tau)
        sequence.add_pulse(np.pi / 2 * h1, 0.0, pulse_type=pulse_type)
        sequence.set_detection(dt, points)
        return sequence


def plot_signals(
    time_axis: np.ndarray,
    signals: Dict[str, np.ndarray],
    title: str = "Spin Echo Signals",
    show_components: bool = True,
):
    """Plot simulation results"""
    import matplotlib.pyplot as plt

    plt.figure(figsize=(10, 6))

    colors = {"sx": "blue", "sy": "red", "sz": "green", "s+": "purple", "s-": "orange"}

    for obs, signal in signals.items():
        color = colors.get(obs, "black")
        if np.iscomplexobj(signal):
            if show_components:
                plt.plot(
                    time_axis,
                    np.real(signal),
                    color=color,
                    linewidth=2,
                    label=f"{obs} (Real)",
                    alpha=0.8,
                )
                plt.plot(
                    time_axis,
                    np.imag(signal),
                    color=color,
                    linewidth=2,
                    linestyle="--",
                    label=f"{obs} (Imag)",
                    alpha=0.6,
                )
            else:
                plt.plot(
                    time_axis,
                    np.abs(signal),
                    color=color,
                    linewidth=2,
                    label=f"|{obs}|",
                    alpha=0.8,
                )
        else:
            plt.plot(time_axis, signal, color=color, linewidth=2, label=obs, alpha=0.8)

    plt.xlabel("Time", fontsize=14)
    plt.ylabel("Signal Amplitude", fontsize=14)
    plt.title(title, fontsize=16, fontweight="bold")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.show()


# Example usage and demonstration
if __name__ == "__main__":
    print("=== Refactored Spin Echo Simulation ===\n")

    # Create simulator
    simulator = SpinEchoSimulator(n_jobs=4)

    # Example 1: Standard Hahn echo using builder
    print("1. Standard Hahn Echo")
    hahn_seq = SequenceBuilder.hahn_echo(tau=5.0, dt=0.01, points=800)
    signals1 = simulator.simulate_sequence(hahn_seq, linewidth=2.0)
    time_axis = np.arange(800) * 0.01
    plot_signals(time_axis, signals1, "Hahn Echo")

    # Example 2: Custom sequence with soft pulses
    print("\n2. Custom sequence with soft pulses")
    custom_seq = (
        PulseSequence("Custom Soft Pulse")
        .add_pulse(np.pi / 2, phase=0.0, pulse_type="soft", duration=2.0)
        .add_delay(3.0)
        .add_pulse(np.pi, phase=np.pi / 2, pulse_type="soft", duration=1.5)
        .add_delay(2.0)
        .add_pulse(np.pi / 4, phase=0.0, pulse_type="hard")
        .set_detection(0.01, 600)
    )

    signals2 = simulator.simulate_sequence(custom_seq, linewidth=1.5)
    time_axis2 = np.arange(600) * 0.01
    plot_signals(time_axis2, signals2, "Custom Soft Pulse Sequence")

    # Example 3: Stimulated echo comparison
    print("\n3. Stimulated Echo")
    stim_seq = SequenceBuilder.stimulated_echo(tau1=3.0, tau2=7.0, dt=0.01, points=800)
    signals3 = simulator.simulate_sequence(stim_seq, linewidth=2.0)
    plot_signals(time_axis, signals3, "Stimulated Echo")

    print("\nAll examples completed!")
