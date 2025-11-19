#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Spin Echo Simulation with Shaped Pulses

Advanced spin echo simulation supporting arbitrary pulse shapes including:
- Gaussian, square, SECH, sinc pulses
- Chirped pulses with frequency sweeps
- WURST pulses for broadband excitation
- Noisy pulses with amplitude/phase fluctuations
- Time-sliced evolution during shaped pulses

@author: sylvainbertaina
"""

import numpy as np
from scipy.linalg import expm
from joblib import Parallel, delayed
from typing import List, Dict, Any, Tuple, Optional, Callable
from dataclasses import dataclass, field
import matplotlib.pyplot as plt

# =============================================================================
# CONSTANTS AND BASIC DEFINITIONS
# =============================================================================

# Pauli matrices (spin-1/2 operators)
SZ = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
SX = 0.5 * np.array([[0, 1], [1, 0]], dtype=complex)
SY = 0.5 * np.array([[0, 1j], [-1j, 0]], dtype=complex)

# =============================================================================
# DATA CLASSES FOR CLEAN PARAMETER HANDLING
# =============================================================================

@dataclass
class PulseShape:
    """
    Defines the time-dependent shape of a pulse.

    Attributes:
    -----------
    amplitude : np.ndarray
        Amplitude envelope over time
    phase : np.ndarray
        Phase modulation over time
    frequency : np.ndarray
        Frequency modulation over time
    time_axis : np.ndarray
        Time points for the pulse
    """
    amplitude: np.ndarray
    phase: np.ndarray
    frequency: np.ndarray
    time_axis: np.ndarray

    def __post_init__(self):
        """Validate that all arrays have the same length."""
        n_points = len(self.time_axis)
        arrays = [self.amplitude, self.phase, self.frequency]
        names = ['amplitude', 'phase', 'frequency']

        for array, name in zip(arrays, names):
            if len(array) != n_points:
                raise ValueError(f"{name} array must match time axis length ({n_points} points)")

@dataclass
class PulseParameters:
    """
    Complete parameters for a shaped pulse operation.

    Attributes:
    -----------
    flip_angle : float
        Target flip angle in radians (e.g., np.pi/2 for 90° pulse)
    duration : float
        Total pulse duration in time units
    shape_type : str
        Pulse shape type: 'gaussian', 'square', 'sech', 'chirp', 'wurst', 'noisy'
    shape_params : Dict[str, Any]
        Shape-specific parameters (e.g., {'sigma_factor': 4.0} for Gaussian)
    phase_offset : float
        Global phase offset in radians
    n_time_slices : int
        Number of time slices for evolution (higher = more accurate)
    sx_amplitude : float
        Relative amplitude for Sx component (real part)
    sy_amplitude : float
        Relative amplitude for Sy component (imaginary part)
    """
    flip_angle: float
    duration: float
    shape_type: str
    shape_params: Dict[str, Any] = field(default_factory=dict)
    phase_offset: float = 0.0
    n_time_slices: int = 100
    sx_amplitude: float = 1.0
    sy_amplitude: float = 0.0

@dataclass
class DetectionParameters:
    """
    Parameters for signal detection.

    Attributes:
    -----------
    dt : float
        Time step between detection points
    points : int
        Number of detection points
    detect_axes : List[str]
        Which observables to detect: 'sx', 'sy', 'sz', 's+', 's-'
    """
    dt: float
    points: int
    detect_axes: List[str] = field(default_factory=lambda: ['sx', 'sy'])

# =============================================================================
# PULSE SHAPE GENERATORS
# =============================================================================

class PulseShapeFactory:
    """
    Factory class for generating various pulse shapes.

    This class provides static methods to create different types of pulse shapes
    commonly used in magnetic resonance experiments.
    """

    @staticmethod
    def gaussian(duration: float, n_points: int, sigma_factor: float = 4.0) -> PulseShape:
        """
        Generate a Gaussian pulse shape.

        Parameters:
        -----------
        duration : float
            Total pulse duration
        n_points : int
            Number of time points
        sigma_factor : float
            Width factor (pulse_width = duration/sigma_factor)

        Returns:
        --------
        PulseShape
            Gaussian pulse shape object
        """
        time_axis = np.linspace(0, duration, n_points)
        t_center = duration / 2
        sigma = duration / sigma_factor

        # Gaussian amplitude envelope
        amplitude = np.exp(-0.5 * ((time_axis - t_center) / sigma) ** 2)

        # Constant phase and zero frequency modulation
        phase = np.zeros_like(time_axis)
        frequency = np.zeros_like(time_axis)

        return PulseShape(amplitude, phase, frequency, time_axis)

    @staticmethod
    def square(duration: float, n_points: int, rise_time: float = 0.0) -> PulseShape:
        """
        Generate a square pulse with optional rise/fall times.

        Parameters:
        -----------
        duration : float
            Total pulse duration
        n_points : int
            Number of time points
        rise_time : float
            Rise/fall time (0 = perfect square)

        Returns:
        --------
        PulseShape
            Square pulse shape object
        """
        time_axis = np.linspace(0, duration, n_points)
        amplitude = np.ones_like(time_axis)

        # Add rise/fall if requested
        if rise_time > 0:
            rise_samples = int(rise_time / duration * n_points)
            if rise_samples > 0:
                # Linear rise
                amplitude[:rise_samples] = np.linspace(0, 1, rise_samples)
                # Linear fall
                amplitude[-rise_samples:] = np.linspace(1, 0, rise_samples)

        phase = np.zeros_like(time_axis)
        frequency = np.zeros_like(time_axis)

        return PulseShape(amplitude, phase, frequency, time_axis)

    @staticmethod
    def sech(duration: float, n_points: int, beta: float = 5.0) -> PulseShape:
        """
        Generate a hyperbolic secant (sech) pulse.

        SECH pulses have self-refocusing properties and are useful for
        adiabatic inversion.

        Parameters:
        -----------
        duration : float
            Total pulse duration
        n_points : int
            Number of time points
        beta : float
            Pulse steepness parameter

        Returns:
        --------
        PulseShape
            SECH pulse shape object
        """
        time_axis = np.linspace(0, duration, n_points)
        t_center = duration / 2

        # SECH amplitude envelope
        amplitude = 1.0 / np.cosh(beta * (time_axis - t_center) / duration)

        phase = np.zeros_like(time_axis)
        frequency = np.zeros_like(time_axis)

        return PulseShape(amplitude, phase, frequency, time_axis)

    @staticmethod
    def wurst(duration: float, n_points: int, freq_start: float, freq_end: float,
              wurst_n: int = 40, amplitude_factor: float = 1.0) -> PulseShape:
        """
        Generate a WURST (Wideband, Uniform Rate, Smooth Truncation) pulse.

        WURST pulses provide excellent broadband inversion with uniform
        excitation over a wide frequency range.

        Parameters:
        -----------
        duration : float
            Total pulse duration
        n_points : int
            Number of time points
        freq_start : float
            Starting frequency of the sweep
        freq_end : float
            Ending frequency of the sweep
        wurst_n : int
            WURST parameter controlling envelope sharpness (typically 20-100)
        amplitude_factor : float
            Overall amplitude scaling factor

        Returns:
        --------
        PulseShape
            WURST pulse shape object
        """
        time_axis = np.linspace(0, duration, n_points)

        # Normalize time to [-1, 1] for WURST envelope
        t_normalized = 2 * time_axis / duration - 1

        # WURST amplitude envelope: (1 - |t|^n)
        amplitude = amplitude_factor * (1 - np.abs(t_normalized) ** wurst_n)
        amplitude = np.maximum(amplitude, 0)  # Ensure non-negative

        # Linear frequency sweep
        frequency = np.linspace(freq_start, freq_end, n_points)

        # Compute phase from frequency sweep
        dt = duration / (n_points - 1) if n_points > 1 else 0
        phase = np.cumsum(frequency) * dt * 2 * np.pi

        return PulseShape(amplitude, phase, frequency, time_axis)

    @staticmethod
    def chirp(duration: float, n_points: int, freq_start: float, freq_end: float,
              envelope: str = 'gaussian', envelope_params: Dict = None) -> PulseShape:
        """
        Generate a chirped pulse with frequency sweep and envelope.

        Parameters:
        -----------
        duration : float
            Total pulse duration
        n_points : int
            Number of time points
        freq_start : float
            Starting frequency
        freq_end : float
            Ending frequency
        envelope : str
            Envelope type: 'gaussian', 'square', 'sech'
        envelope_params : Dict
            Parameters for the envelope

        Returns:
        --------
        PulseShape
            Chirped pulse shape object
        """
        time_axis = np.linspace(0, duration, n_points)

        # Generate frequency sweep
        frequency = np.linspace(freq_start, freq_end, n_points)

        # Compute phase from frequency
        dt = duration / (n_points - 1) if n_points > 1 else 0
        phase = np.cumsum(frequency) * dt * 2 * np.pi

        # Generate envelope
        if envelope_params is None:
            envelope_params = {}

        if envelope == 'gaussian':
            sigma_factor = envelope_params.get('sigma_factor', 4.0)
            envelope_shape = PulseShapeFactory.gaussian(duration, n_points, sigma_factor)
            amplitude = envelope_shape.amplitude
        elif envelope == 'square':
            amplitude = np.ones_like(time_axis)
        elif envelope == 'sech':
            beta = envelope_params.get('beta', 5.0)
            envelope_shape = PulseShapeFactory.sech(duration, n_points, beta)
            amplitude = envelope_shape.amplitude
        else:
            raise ValueError(f"Unknown envelope type: {envelope}")

        return PulseShape(amplitude, phase, frequency, time_axis)

    @staticmethod
    def noisy(duration: float, n_points: int, base_shape: str = 'gaussian',
              amp_noise: float = 0.1, phase_noise: float = 0.1,
              freq_noise: float = 0.0, seed: Optional[int] = None) -> PulseShape:
        """
        Generate a noisy pulse with amplitude/phase/frequency fluctuations.

        Useful for simulating realistic experimental conditions with
        RF instabilities.

        Parameters:
        -----------
        duration : float
            Total pulse duration
        n_points : int
            Number of time points
        base_shape : str
            Base pulse shape: 'gaussian', 'square', 'sech'
        amp_noise : float
            Amplitude noise level (relative)
        phase_noise : float
            Phase noise level (radians)
        freq_noise : float
            Frequency noise level
        seed : Optional[int]
            Random seed for reproducibility

        Returns:
        --------
        PulseShape
            Noisy pulse shape object
        """
        if seed is not None:
            np.random.seed(seed)

        # Generate base shape
        if base_shape == 'gaussian':
            base_pulse = PulseShapeFactory.gaussian(duration, n_points)
        elif base_shape == 'square':
            base_pulse = PulseShapeFactory.square(duration, n_points)
        elif base_shape == 'sech':
            base_pulse = PulseShapeFactory.sech(duration, n_points)
        else:
            raise ValueError(f"Unknown base shape: {base_shape}")

        # Add noise
        amp_fluctuations = 1 + amp_noise * np.random.randn(n_points)
        phase_fluctuations = phase_noise * np.random.randn(n_points)
        freq_fluctuations = freq_noise * np.random.randn(n_points)

        # Apply noise
        amplitude = base_pulse.amplitude * amp_fluctuations
        phase = base_pulse.phase + phase_fluctuations
        frequency = base_pulse.frequency + freq_fluctuations

        # Ensure amplitude is non-negative
        amplitude = np.maximum(amplitude, 0)

        return PulseShape(amplitude, phase, frequency, base_pulse.time_axis)

# =============================================================================
# QUANTUM EVOLUTION ENGINE
# =============================================================================

class QuantumEvolution:
    """
    Handles quantum mechanical evolution during shaped pulses.

    This class implements time-sliced evolution for realistic simulation
    of shaped pulse effects on spin systems.
    """

    @staticmethod
    def evolve_shaped_pulse(initial_state: np.ndarray, pulse_shape: PulseShape,
                           flip_angle: float, detuning: float,
                           sx_amplitude: float = 1.0, sy_amplitude: float = 0.0) -> np.ndarray:
        """
        Evolve a quantum state through a shaped pulse using time slicing.

        This method divides the pulse into small time slices and applies
        the appropriate Hamiltonian evolution for each slice.

        Parameters:
        -----------
        initial_state : np.ndarray
            Input density matrix (2x2 complex array)
        pulse_shape : PulseShape
            Pulse shape definition
        flip_angle : float
            Target flip angle (scales the pulse amplitude)
        detuning : float
            Frequency detuning from resonance
        sx_amplitude : float
            Relative amplitude for Sx component (real part)
        sy_amplitude : float
            Relative amplitude for Sy component (imaginary part)

        Returns:
        --------
        np.ndarray
            Evolved density matrix
        """
        n_slices = len(pulse_shape.time_axis)
        if n_slices < 2:
            return initial_state.copy()

        dt = pulse_shape.time_axis[1] - pulse_shape.time_axis[0]

        # Calculate amplitude scaling to achieve target flip angle
        amplitude_scale = QuantumEvolution._calculate_amplitude_scaling(
            pulse_shape.amplitude, pulse_shape.time_axis, flip_angle)

        # Normalize multi-axis amplitudes
        sx_norm, sy_norm = QuantumEvolution._normalize_multiaxis_amplitudes(
            sx_amplitude, sy_amplitude)

        # Evolve through each time slice
        current_state = initial_state.copy()

        for i in range(n_slices - 1):
            current_state = QuantumEvolution._evolve_single_slice(
                current_state, pulse_shape, i, dt, amplitude_scale,
                detuning, sx_norm, sy_norm)

        return current_state

    @staticmethod
    def _calculate_amplitude_scaling(amplitude: np.ndarray, time_axis: np.ndarray,
                                   flip_angle: float) -> float:
        """Calculate scaling factor to achieve target flip angle."""
        integral_amplitude = np.trapezoid(amplitude, time_axis)
        return flip_angle / integral_amplitude if integral_amplitude > 1e-12 else 0.0

    @staticmethod
    def _normalize_multiaxis_amplitudes(sx_amp: float, sy_amp: float) -> Tuple[float, float]:
        """Normalize Sx and Sy amplitudes."""
        total_amplitude = np.sqrt(sx_amp**2 + sy_amp**2)
        if total_amplitude > 1e-12:
            return sx_amp / total_amplitude, sy_amp / total_amplitude
        else:
            return 1.0, 0.0

    @staticmethod
    def _evolve_single_slice(state: np.ndarray, pulse_shape: PulseShape,
                           slice_idx: int, dt: float, amplitude_scale: float,
                           detuning: float, sx_norm: float, sy_norm: float) -> np.ndarray:
        """Evolve state through a single time slice."""
        # Get pulse parameters for this slice
        amp = pulse_shape.amplitude[slice_idx] * amplitude_scale
        phase = pulse_shape.phase[slice_idx]
        freq_offset = pulse_shape.frequency[slice_idx]

        # Build Hamiltonian for this slice
        H_total = QuantumEvolution._build_slice_hamiltonian(
            amp, phase, freq_offset, detuning, dt, sx_norm, sy_norm)

        # Apply evolution operator
        if np.any(np.abs(H_total) > 1e-12):
            U_slice = expm(-1j * H_total * dt)
            return U_slice.conj().T @ state @ U_slice
        else:
            return state

    @staticmethod
    def _build_slice_hamiltonian(amp: float, phase: float, freq_offset: float,
                               detuning: float, dt: float, sx_norm: float,
                               sy_norm: float) -> np.ndarray:
        """Build the Hamiltonian for a single time slice."""
        H_total = np.zeros((2, 2), dtype=complex)

        # RF Hamiltonian (if pulse is on)
        if abs(amp) > 1e-12:
            # Phase-rotated Sx and Sy operators
            sx_rotated = np.cos(phase) * SX - np.sin(phase) * SY
            sy_rotated = np.sin(phase) * SX + np.cos(phase) * SY

            # Multi-axis RF operator
            rf_operator = sx_norm * sx_rotated + sy_norm * sy_rotated
            # Use amplitude directly - the amplitude_scale already accounts for duration
            H_total += amp * rf_operator

        # Detuning Hamiltonian (always present) - this is the Sz evolution!
        total_detuning = detuning + freq_offset
        if abs(total_detuning) > 1e-12:
            H_total += total_detuning * SZ

        return H_total

    @staticmethod
    def evolve_free_precession(state: np.ndarray, duration: float,
                             detuning: float) -> np.ndarray:
        """
        Evolve state during free precession (delay).

        Parameters:
        -----------
        state : np.ndarray
            Input density matrix
        duration : float
            Duration of free precession
        detuning : float
            Frequency detuning

        Returns:
        --------
        np.ndarray
            Evolved density matrix
        """
        if abs(detuning * duration) > 1e-12:
            U_delay = expm(-1j * detuning * SZ * duration)
            return U_delay.conj().T @ state @ U_delay
        return state

# =============================================================================
# SEQUENCE OPERATIONS
# =============================================================================

class SequenceOperation:
    """Base class for sequence operations."""

    def execute(self, state: np.ndarray, detuning: float) -> np.ndarray:
        """Execute the operation on a quantum state."""
        raise NotImplementedError("Subclasses must implement execute method")

class ShapedPulse(SequenceOperation):
    """
    A shaped pulse operation in a pulse sequence.

    This class encapsulates all parameters needed for a shaped pulse
    and can execute the pulse on a quantum state.
    """

    def __init__(self, params: PulseParameters):
        """
        Initialize shaped pulse operation.

        Parameters:
        -----------
        params : PulseParameters
            Complete pulse parameters
        """
        self.params = params
        self._pulse_shape_cache = None  # Cache for generated pulse shape

    def get_pulse_shape(self) -> PulseShape:
        """
        Get the pulse shape, generating it if needed.

        Returns:
        --------
        PulseShape
            The pulse shape object
        """
        if self._pulse_shape_cache is None:
            self._pulse_shape_cache = self._generate_pulse_shape()
        return self._pulse_shape_cache

    def _generate_pulse_shape(self) -> PulseShape:
        """Generate pulse shape based on parameters."""
        shape_type = self.params.shape_type
        duration = self.params.duration
        n_points = self.params.n_time_slices
        params = self.params.shape_params

        # Dispatch to appropriate factory method
        if shape_type == 'gaussian':
            sigma_factor = params.get('sigma_factor', 4.0)
            return PulseShapeFactory.gaussian(duration, n_points, sigma_factor)

        elif shape_type == 'square':
            rise_time = params.get('rise_time', 0.0)
            return PulseShapeFactory.square(duration, n_points, rise_time)

        elif shape_type == 'sech':
            beta = params.get('beta', 5.0)
            return PulseShapeFactory.sech(duration, n_points, beta)

        elif shape_type == 'wurst':
            freq_start = params.get('freq_start', -5.0)
            freq_end = params.get('freq_end', 5.0)
            wurst_n = params.get('wurst_n', 40)
            amplitude_factor = params.get('amplitude_factor', 1.0)
            return PulseShapeFactory.wurst(duration, n_points, freq_start,
                                         freq_end, wurst_n, amplitude_factor)

        elif shape_type == 'chirp':
            freq_start = params.get('freq_start', -5.0)
            freq_end = params.get('freq_end', 5.0)
            envelope = params.get('envelope', 'gaussian')
            envelope_params = params.get('envelope_params', {})
            return PulseShapeFactory.chirp(duration, n_points, freq_start,
                                         freq_end, envelope, envelope_params)

        elif shape_type == 'noisy':
            base_shape = params.get('base_shape', 'gaussian')
            amp_noise = params.get('amp_noise', 0.1)
            phase_noise = params.get('phase_noise', 0.1)
            freq_noise = params.get('freq_noise', 0.0)
            seed = params.get('seed', None)
            return PulseShapeFactory.noisy(duration, n_points, base_shape,
                                         amp_noise, phase_noise, freq_noise, seed)
        else:
            raise ValueError(f"Unknown pulse shape type: {shape_type}")

    def execute(self, state: np.ndarray, detuning: float) -> np.ndarray:
        """
        Execute the shaped pulse on a quantum state.

        Parameters:
        -----------
        state : np.ndarray
            Input density matrix
        detuning : float
            Frequency detuning

        Returns:
        --------
        np.ndarray
            Evolved density matrix
        """
        pulse_shape = self.get_pulse_shape()

        # Apply global phase offset if needed
        if abs(self.params.phase_offset) > 1e-12:
            pulse_shape = PulseShape(
                pulse_shape.amplitude,
                pulse_shape.phase + self.params.phase_offset,
                pulse_shape.frequency,
                pulse_shape.time_axis
            )

        return QuantumEvolution.evolve_shaped_pulse(
            state, pulse_shape, self.params.flip_angle, detuning,
            self.params.sx_amplitude, self.params.sy_amplitude)

class Delay(SequenceOperation):
    """
    A delay (free precession) operation in a pulse sequence.
    """

    def __init__(self, duration: float):
        """
        Initialize delay operation.

        Parameters:
        -----------
        duration : float
            Duration of the delay
        """
        self.duration = duration

    def execute(self, state: np.ndarray, detuning: float) -> np.ndarray:
        """
        Execute the delay operation.

        Parameters:
        -----------
        state : np.ndarray
            Input density matrix
        detuning : float
            Frequency detuning

        Returns:
        --------
        np.ndarray
            Evolved density matrix after free precession
        """
        return QuantumEvolution.evolve_free_precession(state, self.duration, detuning)

# =============================================================================
# MAIN SEQUENCE CLASS
# =============================================================================

class ShapedPulseSequence:
    """
    A complete pulse sequence with shaped pulses and delays.

    This class uses a builder pattern to construct pulse sequences step by step.
    Each method returns self to allow method chaining.
    """

    def __init__(self, name: str = "Shaped Sequence"):
        """
        Initialize an empty pulse sequence.

        Parameters:
        -----------
        name : str
            Name of the sequence for identification
        """
        self.name = name
        self.operations: List[SequenceOperation] = []
        self.detection_params: Optional[DetectionParameters] = None

    def add_shaped_pulse(self, flip_angle: float, duration: float, shape_type: str,
                        shape_params: Dict = None, phase_offset: float = 0.0,
                        n_time_slices: int = 100, sx_amplitude: float = 1.0,
                        sy_amplitude: float = 0.0) -> 'ShapedPulseSequence':
        """
        Add a shaped pulse to the sequence.

        Parameters:
        -----------
        flip_angle : float
            Target flip angle in radians (e.g., np.pi/2 for 90°)
        duration : float
            Pulse duration
        shape_type : str
            Type of pulse shape: 'gaussian', 'square', 'sech', 'wurst', 'chirp', 'noisy'
        shape_params : Dict, optional
            Shape-specific parameters
        phase_offset : float, optional
            Global phase offset in radians
        n_time_slices : int, optional
            Number of time slices for evolution
        sx_amplitude : float, optional
            Relative amplitude for Sx component
        sy_amplitude : float, optional
            Relative amplitude for Sy component

        Returns:
        --------
        ShapedPulseSequence
            Self (for method chaining)
        """
        if shape_params is None:
            shape_params = {}

        params = PulseParameters(
            flip_angle=flip_angle,
            duration=duration,
            shape_type=shape_type,
            shape_params=shape_params,
            phase_offset=phase_offset,
            n_time_slices=n_time_slices,
            sx_amplitude=sx_amplitude,
            sy_amplitude=sy_amplitude
        )

        self.operations.append(ShapedPulse(params))
        return self

    def add_delay(self, duration: float) -> 'ShapedPulseSequence':
        """
        Add a delay (free precession) to the sequence.

        Parameters:
        -----------
        duration : float
            Duration of the delay

        Returns:
        --------
        ShapedPulseSequence
            Self (for method chaining)
        """
        self.operations.append(Delay(duration))
        return self

    def set_detection(self, dt: float, points: int,
                     detect_axes: List[str] = None) -> 'ShapedPulseSequence':
        """
        Set parameters for signal detection.

        Parameters:
        -----------
        dt : float
            Time step between detection points
        points : int
            Number of detection points
        detect_axes : List[str], optional
            Observables to detect: 'sx', 'sy', 'sz', 's+', 's-'

        Returns:
        --------
        ShapedPulseSequence
            Self (for method chaining)
        """
        if detect_axes is None:
            detect_axes = ['sx', 'sy']

        self.detection_params = DetectionParameters(
            dt=dt,
            points=points,
            detect_axes=detect_axes
        )
        return self

    def simulate_single_detuning(self, detuning: float,
                               initial_state: Optional[np.ndarray] = None) -> Dict[str, np.ndarray]:
        """
        Simulate the sequence for a single detuning value.

        Parameters:
        -----------
        detuning : float
            Frequency detuning value
        initial_state : np.ndarray, optional
            Initial density matrix (default: thermal equilibrium along z)

        Returns:
        --------
        Dict[str, np.ndarray]
            Dictionary of detected signals
        """
        if self.detection_params is None:
            raise ValueError("Detection parameters must be set before simulation")

        # Initialize state
        if initial_state is None:
            current_state = SZ.copy()  # Thermal equilibrium
        else:
            current_state = initial_state.copy()

        # Execute all operations in sequence
        for operation in self.operations:
            current_state = operation.execute(current_state, detuning)

        # Perform detection
        return self._detect_signals(current_state, detuning)

    def _detect_signals(self, final_state: np.ndarray, detuning: float) -> Dict[str, np.ndarray]:
        """Detect signals after sequence execution."""
        dt = self.detection_params.dt
        points = self.detection_params.points
        detect_axes = self.detection_params.detect_axes

        # Initialize signal arrays
        signals = {}
        for axis in detect_axes:
            dtype = complex if axis in ['s+', 's-'] else float
            signals[axis] = np.zeros(points, dtype=dtype)

        # Evolution operator for detection
        U_evolution = expm(-1j * detuning * SZ * dt)
        current_state = final_state.copy()

        # Detect at each time point
        for t in range(points):
            for axis in detect_axes:
                signals[axis][t] = self._measure_observable(current_state, axis)

            # Evolve for next time point
            current_state = U_evolution.conj().T @ current_state @ U_evolution

        return signals

    def _measure_observable(self, state: np.ndarray, observable: str) -> complex:
        """Measure a specific observable on the state."""
        if observable == 'sx':
            return np.real(np.trace(state @ SX))
        elif observable == 'sy':
            return np.real(np.trace(state @ SY))
        elif observable == 'sz':
            return np.real(np.trace(state @ SZ))
        elif observable == 's+':
            return np.trace(state @ (SX + 1j * SY))
        elif observable == 's-':
            return np.trace(state @ (SX - 1j * SY))
        else:
            raise ValueError(f"Unknown observable: {observable}")

# =============================================================================
# MAIN SIMULATOR CLASS
# =============================================================================

class ShapedSpinEchoSimulator:
    """
    Main simulator for shaped pulse sequences over multiple detuning values.

    This class handles parallel simulation over a range of detuning values
    and applies appropriate line shape weighting.
    """

    def __init__(self, n_jobs: int = 1):
        """
        Initialize the simulator.

        Parameters:
        -----------
        n_jobs : int
            Number of parallel jobs (-1 for all cores, 1 for serial)
        """
        self.n_jobs = n_jobs

    def simulate_sequence(self, sequence: ShapedPulseSequence,
                         detuning_range: Tuple[float, float] = (-10.0, 10.0),
                         detuning_points: int = 101,
                         linewidth: float = 2.0,
                         distribution_type: str = "gaussian") -> Dict[str, np.ndarray]:
        """
        Simulate a shaped pulse sequence over a range of detuning values.

        Parameters:
        -----------
        sequence : ShapedPulseSequence
            The pulse sequence to simulate
        detuning_range : Tuple[float, float]
            Range of detuning values (min, max)
        detuning_points : int
            Number of detuning points to simulate
        linewidth : float
            Spectral linewidth parameter
        distribution_type : str
            Line shape: "gaussian", "lorentzian", or "uniform"

        Returns:
        --------
        Dict[str, np.ndarray]
            Dictionary of weighted, averaged signals
        """
        # Generate detuning values and weights
        detuning_values, weights = self._generate_detuning_distribution(
            detuning_range, detuning_points, linewidth, distribution_type)

        # Parallel simulation over all detuning values
        if self.n_jobs == 1:
            # Serial execution for debugging
            results_list = [sequence.simulate_single_detuning(delta)
                          for delta in detuning_values]
        else:
            # Parallel execution
            results_list = Parallel(n_jobs=self.n_jobs, verbose=1)(
                delayed(sequence.simulate_single_detuning)(delta)
                for delta in detuning_values)

        # Aggregate results with proper weighting
        return self._aggregate_results(results_list, weights, sequence.detection_params.detect_axes)

    def _generate_detuning_distribution(self, detuning_range: Tuple[float, float],
                                      n_points: int, linewidth: float,
                                      distribution_type: str) -> Tuple[np.ndarray, np.ndarray]:
        """Generate detuning values and corresponding weights."""
        detuning_values = np.linspace(detuning_range[0], detuning_range[1], n_points)

        if distribution_type == "gaussian":
            weights = np.exp(-(detuning_values / linewidth) ** 2)
        elif distribution_type == "lorentzian":
            weights = 1.0 / (1.0 + (detuning_values / linewidth) ** 2)
        elif distribution_type == "uniform":
            weights = np.ones_like(detuning_values)
        else:
            raise ValueError(f"Unknown distribution type: {distribution_type}")

        # Normalize weights
        weights = weights / np.sum(weights)

        return detuning_values, weights

    def _aggregate_results(self, results_list: List[Dict], weights: np.ndarray,
                         observables: List[str]) -> Dict[str, np.ndarray]:
        """Aggregate simulation results with proper weighting."""
        final_signals = {}

        for obs in observables:
            # Stack all results for this observable
            signals_array = np.array([result[obs] for result in results_list])

            # Apply weighting and sum
            weighted_signals = signals_array.T * weights
            final_signals[obs] = np.sum(weighted_signals, axis=1)

        return final_signals

# =============================================================================
# CONVENIENCE FUNCTIONS AND BUILDERS
# =============================================================================

class SequenceBuilder:
    """
    Factory class for common pulse sequences.

    Provides pre-configured sequences for typical NMR/ESR experiments.
    """

    @staticmethod
    def hahn_echo(tau: float, pulse_duration: float = 1.0,
                  pulse_shape: str = 'gaussian', shape_params: Dict = None,
                  dt: float = 0.01, points: int = 800) -> ShapedPulseSequence:
        """
        Create a Hahn echo sequence: π/2 - τ - π.

        Parameters:
        -----------
        tau : float
            Echo delay time
        pulse_duration : float
            Duration of each pulse
        pulse_shape : str
            Type of pulse shape
        shape_params : Dict, optional
            Shape-specific parameters
        dt : float
            Detection time step
        points : int
            Number of detection points

        Returns:
        --------
        ShapedPulseSequence
            Complete Hahn echo sequence
        """
        if shape_params is None:
            shape_params = {'sigma_factor': 4.0} if pulse_shape == 'gaussian' else {}

        return (ShapedPulseSequence("Hahn Echo")
                .add_shaped_pulse(np.pi/2, pulse_duration, pulse_shape, shape_params)
                .add_delay(tau)
                .add_shaped_pulse(np.pi, pulse_duration, pulse_shape, shape_params)
                .set_detection(dt, points))

    @staticmethod
    def wurst_echo(tau: float, pulse_duration: float = 2.0,
                   freq_start: float = -8.0, freq_end: float = 8.0,
                   wurst_n: int = 40, dt: float = 0.01, points: int = 800) -> ShapedPulseSequence:
        """
        Create a WURST echo sequence for broadband excitation.

        Parameters:
        -----------
        tau : float
            Echo delay time
        pulse_duration : float
            Duration of each WURST pulse
        freq_start : float
            Starting frequency of WURST sweep
        freq_end : float
            Ending frequency of WURST sweep
        wurst_n : int
            WURST envelope parameter
        dt : float
            Detection time step
        points : int
            Number of detection points

        Returns:
        --------
        ShapedPulseSequence
            Complete WURST echo sequence
        """
        wurst_params = {
            'freq_start': freq_start,
            'freq_end': freq_end,
            'wurst_n': wurst_n
        }

        return (ShapedPulseSequence("WURST Echo")
                .add_shaped_pulse(np.pi/2, pulse_duration, 'wurst', wurst_params)
                .add_delay(tau)
                .add_shaped_pulse(np.pi, pulse_duration, 'wurst', wurst_params)
                .set_detection(dt, points))

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def plot_pulse_shape(pulse_shape: PulseShape, title: str = "Pulse Shape") -> None:
    """
    Plot the components of a pulse shape.

    Parameters:
    -----------
    pulse_shape : PulseShape
        Pulse shape to plot
    title : str
        Plot title
    """
    fig, axes = plt.subplots(3, 1, figsize=(10, 8), sharex=True)

    # Amplitude
    axes[0].plot(pulse_shape.time_axis, pulse_shape.amplitude, 'b-', linewidth=2)
    axes[0].set_ylabel('Amplitude')
    axes[0].set_title(title)
    axes[0].grid(True, alpha=0.3)

    # Phase
    axes[1].plot(pulse_shape.time_axis, pulse_shape.phase, 'r-', linewidth=2)
    axes[1].set_ylabel('Phase (rad)')
    axes[1].grid(True, alpha=0.3)

    # Frequency
    axes[2].plot(pulse_shape.time_axis, pulse_shape.frequency, 'g-', linewidth=2)
    axes[2].set_ylabel('Frequency')
    axes[2].set_xlabel('Time')
    axes[2].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    print("=== Shaped Pulse Spin Echo Simulation ===\n")

    # Create simulator
    simulator = ShapedSpinEchoSimulator(n_jobs=2)

    # Example 1: Gaussian Hahn echo
    print("1. Gaussian Hahn echo")
    gaussian_seq = SequenceBuilder.hahn_echo(tau=5.0, pulse_duration=1.0,
                                           pulse_shape='gaussian')

    # Visualize pulse shape
    gaussian_pulse = gaussian_seq.operations[0].get_pulse_shape()
    plot_pulse_shape(gaussian_pulse, "Gaussian π/2 Pulse")

    # Simulate
    signals1 = simulator.simulate_sequence(gaussian_seq, linewidth=2.0, detuning_points=51)

    # Example 2: WURST echo
    print("\n2. WURST echo")
    wurst_seq = SequenceBuilder.wurst_echo(tau=5.0, pulse_duration=2.0,
                                         freq_start=-5.0, freq_end=5.0)

    # Visualize pulse shape
    wurst_pulse = wurst_seq.operations[0].get_pulse_shape()
    plot_pulse_shape(wurst_pulse, "WURST π/2 Pulse")

    # Simulate
    signals2 = simulator.simulate_sequence(wurst_seq, linewidth=2.0, detuning_points=51)

    # Plot comparison
    time_axis = np.arange(800) * 0.01

    plt.figure(figsize=(12, 6))

    plt.subplot(1, 2, 1)
    plt.plot(time_axis, np.real(signals1['sx']), 'b-', label='Gaussian Sx')
    plt.plot(time_axis, np.real(signals1['sy']), 'r-', label='Gaussian Sy')
    plt.xlabel('Time')
    plt.ylabel('Signal')
    plt.title('Gaussian Echo')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.subplot(1, 2, 2)
    plt.plot(time_axis, np.real(signals2['sx']), 'b-', label='WURST Sx')
    plt.plot(time_axis, np.real(signals2['sy']), 'r-', label='WURST Sy')
    plt.xlabel('Time')
    plt.ylabel('Signal')
    plt.title('WURST Echo')
    plt.legend()
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()

    print("\n✅ Shaped pulse simulation completed!")