#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Interface for 2-Pulse Spin Echo Simulation

Tkinter interface allowing real-time modification of all parameters
and immediate visualization of the effect on the echo signal.

@author: sylvainbertaina
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import numpy as np
from scipy.linalg import expm
import threading
import time

# Pauli matrices
sz = 0.5 * np.array([[1, 0], [0, -1]], dtype=complex)
sx = 0.5 * np.array([[0, 1], [1, 0]], dtype=complex)
sy = 0.5 * np.array([[0, 1j], [-1j, 0]], dtype=complex)

def evolution_operator(theta_x, theta_z, phase=0.0):
    """Create evolution operator"""
    if abs(theta_x) > 1e-12:
        cos_half = np.cos(theta_x/2)
        sin_half = np.sin(theta_x/2)
        if abs(phase) > 1e-12:
            pulse_op = np.cos(phase) * sx + np.sin(phase) * sy
        else:
            pulse_op = sx
        Ux = cos_half * np.eye(2, dtype=complex) - 1j * sin_half * pulse_op
    else:
        Ux = np.eye(2, dtype=complex)

    if abs(theta_z) > 1e-12:
        Uz = expm(-1j * theta_z * sz)
    else:
        Uz = np.eye(2, dtype=complex)

    return Uz @ Ux

def apply_pulse(rho, theta_x, delta, pulse_duration, pulse_type="hard", phase=0.0):
    """Apply a pulse to the density matrix"""
    if pulse_type == "hard":
        U = evolution_operator(theta_x, 0, phase)
        return U.conj().T @ rho @ U
    else:  # soft pulse
        theta_z = delta * pulse_duration
        if abs(phase) > 1e-12:
            pulse_op = np.cos(phase) * sx + np.sin(phase) * sy
        else:
            pulse_op = sx
        H_total = (theta_x / pulse_duration) * pulse_op + delta * sz
        U_soft = expm(-1j * H_total * pulse_duration)
        return U_soft.conj().T @ rho @ U_soft

def spin_distribution(delta_values, linewidth, distri_type="gaussian"):
    """Calculate spin packet distribution weights"""
    if distri_type == "gaussian":
        return np.exp(-(delta_values / linewidth) ** 2)
    elif distri_type == "lorentzian":
        return 1.0 / (1.0 + (delta_values / linewidth) ** 2)
    elif distri_type == "exponential":
        return np.exp(-np.abs(delta_values) / linewidth)
    elif distri_type == "uniform":
        return np.where(np.abs(delta_values) <= linewidth, 1.0, 0.0)

def two_pulse_hahn(delta, dt, tp, tau, points, pulse_type="hard", pulse_duration=None, h1=1.0,
                  phase_pi2=0.0, phase_pi=0.0):
    """Two-pulse Hahn echo simulation

    Parameters:
    -----------
    h1 : float
        Microwave field amplitude (1.0 = perfect π/2 and π pulses)
    phase_pi2 : float
        Phase of π/2 pulse (radians)
    phase_pi : float
        Phase of π pulse (radians)
    """
    tp_eff = pulse_duration if pulse_duration else tp

    rho = sz.copy()

    # π/2 pulse with h1 amplitude scaling and phase
    theta_pi2 = (np.pi/2) * h1
    rho = apply_pulse(rho, theta_pi2, delta, tp_eff, pulse_type, phase=phase_pi2)

    # τ delay
    U_delay = evolution_operator(0, delta * tau, 0)
    rho = U_delay.conj().T @ rho @ U_delay

    # π pulse with h1 amplitude scaling and phase
    theta_pi = np.pi * h1
    rho = apply_pulse(rho, theta_pi, delta, tp_eff, pulse_type, phase=phase_pi)

    # Detection
    U_evolution = evolution_operator(0, delta * dt, 0)
    signal_x = np.zeros(points, dtype=float)  # Sx component
    signal_y = np.zeros(points, dtype=float)  # Sy component

    for t in range(points):
        # Measure x and y magnetization separately
        signal_x[t] = np.real(np.trace(rho @ sx))  # <Sx>
        signal_y[t] = np.real(np.trace(rho @ sy))  # <Sy>
        rho = U_evolution.conj().T @ rho @ U_evolution

    return signal_x, signal_y

def three_pulse_sequence(delta, dt, tp, tau1, tau2, points, pulse_type="hard", pulse_duration=None, h1=1.0,
                        phase_pi2_1=0.0, phase_pi2_2=0.0, phase_pi2_3=0.0):
    """Three-pulse stimulated echo simulation: π/2 - τ1 - π/2 - τ2 - π/2

    Parameters:
    -----------
    h1 : float
        Microwave field amplitude (1.0 = perfect π/2 pulses)
    phase_pi2_1 : float
        Phase of first π/2 pulse (radians)
    phase_pi2_2 : float
        Phase of second π/2 pulse (radians)
    phase_pi2_3 : float
        Phase of third π/2 pulse (radians)
    """
    tp_eff = pulse_duration if pulse_duration else tp

    rho = sz.copy()

    # First π/2 pulse
    theta_pi2 = (np.pi/2) * h1
    rho = apply_pulse(rho, theta_pi2, delta, tp_eff, pulse_type, phase=phase_pi2_1)

    # τ1 delay
    U_delay1 = evolution_operator(0, delta * tau1, 0)
    rho = U_delay1.conj().T @ rho @ U_delay1

    # Second π/2 pulse
    rho = apply_pulse(rho, theta_pi2, delta, tp_eff, pulse_type, phase=phase_pi2_2)

    # τ2 delay
    U_delay2 = evolution_operator(0, delta * tau2, 0)
    rho = U_delay2.conj().T @ rho @ U_delay2

    # Third π/2 pulse
    rho = apply_pulse(rho, theta_pi2, delta, tp_eff, pulse_type, phase=phase_pi2_3)

    # Detection
    U_evolution = evolution_operator(0, delta * dt, 0)
    signal_x = np.zeros(points, dtype=float)  # Sx component
    signal_y = np.zeros(points, dtype=float)  # Sy component

    for t in range(points):
        # Measure x and y magnetization separately
        signal_x[t] = np.real(np.trace(rho @ sx))  # <Sx>
        signal_y[t] = np.real(np.trace(rho @ sy))  # <Sy>
        rho = U_evolution.conj().T @ rho @ U_evolution

    return signal_x, signal_y

class SpinEchoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive Spin Echo Simulation (Single Core)")
        self.root.geometry("1600x1000")

        # Flag for calculation thread (must be set before any calculation)
        self.calculation_running = False

        # Variables for parameters
        self.setup_variables()

        # Create GUI
        self.create_widgets()

        # Initial calculation
        self.calculate_and_plot()

        # Start periodic formatting (every 500ms)
        self._periodic_format()

    def _periodic_format(self):
        """Periodically format all variables to maintain 4-digit display"""
        self._format_all_variables()
        self.root.after(500, self._periodic_format)

    def setup_variables(self):
        """Initialize all parameter variables"""
        # Simulation parameters
        self.dt = tk.DoubleVar(value=0.01)
        self.tp = tk.DoubleVar(value=1.0)
        self.tau = tk.DoubleVar(value=5.0)
        self.tau1 = tk.DoubleVar(value=3.0)  # For 3-pulse sequence
        self.tau2 = tk.DoubleVar(value=8.0)  # For 3-pulse sequence
        self.points = tk.IntVar(value=800)
        self.detuning_points = tk.IntVar(value=101)
        self.linewidth = tk.DoubleVar(value=2.0)
        self.detuning_min = tk.DoubleVar(value=-10.0)
        self.detuning_max = tk.DoubleVar(value=10.0)

        # Sequence selection
        self.sequence_type = tk.StringVar(value="2pulse")

        # Pulse parameters
        self.pulse_type = tk.StringVar(value="hard")
        self.pulse_duration = tk.DoubleVar(value=2.0)
        self.use_custom_duration = tk.BooleanVar(value=False)
        self.h1 = tk.DoubleVar(value=1.0)  # Microwave field amplitude

        # 2-pulse phases
        self.phase_pi2 = tk.DoubleVar(value=0.0)  # π/2 pulse phase (degrees)
        self.phase_pi = tk.DoubleVar(value=0.0)   # π pulse phase (degrees)

        # 3-pulse phases
        self.phase_pi2_1 = tk.DoubleVar(value=0.0)   # First π/2 pulse phase (degrees)
        self.phase_pi2_2 = tk.DoubleVar(value=90.0)  # Second π/2 pulse phase (degrees)
        self.phase_pi2_3 = tk.DoubleVar(value=0.0)   # Third π/2 pulse phase (degrees)

        # Distribution parameters
        self.distri_type = tk.StringVar(value="gaussian")

        # Display options
        self.show_sx = tk.BooleanVar(value=True)
        self.show_sy = tk.BooleanVar(value=True)
        self.show_abs = tk.BooleanVar(value=False)
        self.auto_update = tk.BooleanVar(value=True)
        self.auto_scale = tk.BooleanVar(value=True)

        # Manual axis limits
        self.x_min = tk.DoubleVar(value=0.0)
        self.x_max = tk.DoubleVar(value=20.0)
        self.y_min = tk.DoubleVar(value=-1.0)
        self.y_max = tk.DoubleVar(value=1.0)

        # Collect all DoubleVar for periodic formatting
        self._double_vars = [
            self.dt, self.tp, self.tau, self.tau1, self.tau2,
            self.linewidth, self.detuning_min, self.detuning_max,
            self.pulse_duration, self.h1,
            self.phase_pi2, self.phase_pi,
            self.phase_pi2_1, self.phase_pi2_2, self.phase_pi2_3,
            self.x_min, self.x_max, self.y_min, self.y_max
        ]

        # Flag to prevent recursive formatting
        self._formatting_in_progress = False

    def _format_number(self, value, precision=4):
        """Format number to specified precision (significant figures)"""
        try:
            # Use .4g format for 4 significant figures
            formatted = f"{float(value):.{precision}g}"
            return float(formatted)
        except:
            return value

    def _format_all_variables(self):
        """Format all DoubleVar variables to 4 significant figures"""
        if self._formatting_in_progress:
            return

        self._formatting_in_progress = True
        try:
            for var in self._double_vars:
                try:
                    current = var.get()
                    formatted = self._format_number(current)
                    if abs(current - formatted) > 1e-10:
                        var.set(formatted)
                except:
                    pass
        finally:
            self._formatting_in_progress = False

    def _create_formatted_callback(self, var, original_callback):
        """Create a callback wrapper that formats values before calling original callback"""
        def formatted_callback(value=None):
            self._format_all_variables()
            if original_callback:
                original_callback(value)
        return formatted_callback

    def create_widgets(self):
        """Create all GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Left panel for controls
        control_frame = ttk.Frame(main_frame, width=350)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        control_frame.pack_propagate(False)

        # Right panel for plot
        plot_frame = ttk.Frame(main_frame)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Create control sections
        self.create_simulation_controls(control_frame)
        self.create_pulse_controls(control_frame)
        self.create_distribution_controls(control_frame)
        self.create_display_controls(control_frame)
        self.create_action_buttons(control_frame)

        # Create plot
        self.create_plot(plot_frame)

    def create_simulation_controls(self, parent):
        """Create simulation parameter controls"""
        frame = ttk.LabelFrame(parent, text="Simulation Parameters", padding=10)
        frame.pack(fill=tk.X, pady=(0, 5))

        # Sequence type selection
        ttk.Label(frame, text="Sequence type:").grid(row=0, column=0, sticky=tk.W)
        sequence_combo = ttk.Combobox(frame, textvariable=self.sequence_type,
                                     values=["2pulse", "3pulse"], width=15)
        sequence_combo.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5)
        sequence_combo.bind('<<ComboboxSelected>>', self.on_sequence_change)

        # Time step
        ttk.Label(frame, text="Time step (dt):").grid(row=1, column=0, sticky=tk.W)
        dt_scale = ttk.Scale(frame, from_=0.001, to=0.1, variable=self.dt,
                            orient=tk.HORIZONTAL, length=200, command=self._create_formatted_callback(self.dt, self.on_parameter_change))
        dt_scale.grid(row=1, column=1, sticky=tk.EW, padx=5)
        dt_entry = ttk.Entry(frame, textvariable=self.dt, width=8)
        dt_entry.grid(row=1, column=2)
        dt_entry.bind('<Return>', self.on_parameter_change)

        # Pulse duration
        ttk.Label(frame, text="Pulse duration (tp):").grid(row=2, column=0, sticky=tk.W)
        tp_scale = ttk.Scale(frame, from_=0.1, to=10.0, variable=self.tp,
                            orient=tk.HORIZONTAL, length=200, command=self._create_formatted_callback(self.tp, self.on_parameter_change))
        tp_scale.grid(row=2, column=1, sticky=tk.EW, padx=5)
        tp_entry = ttk.Entry(frame, textvariable=self.tp, width=8)
        tp_entry.grid(row=2, column=2)
        tp_entry.bind('<Return>', self.on_parameter_change)

        # Echo delay (for 2-pulse)
        self.tau_label = ttk.Label(frame, text="Echo delay (τ):")
        self.tau_label.grid(row=3, column=0, sticky=tk.W)
        self.tau_scale = ttk.Scale(frame, from_=0.1, to=20.0, variable=self.tau,
                                  orient=tk.HORIZONTAL, length=200, command=self._create_formatted_callback(self.tau, self.on_parameter_change))
        self.tau_scale.grid(row=3, column=1, sticky=tk.EW, padx=5)
        self.tau_entry = ttk.Entry(frame, textvariable=self.tau, width=8)
        self.tau_entry.grid(row=3, column=2)
        self.tau_entry.bind('<Return>', self.on_parameter_change)

        # τ1 delay (for 3-pulse)
        self.tau1_label = ttk.Label(frame, text="First delay (τ1):")
        self.tau1_scale = ttk.Scale(frame, from_=0.1, to=20.0, variable=self.tau1,
                                   orient=tk.HORIZONTAL, length=200, command=self._create_formatted_callback(self.tau1, self.on_parameter_change))
        self.tau1_entry = ttk.Entry(frame, textvariable=self.tau1, width=8)
        self.tau1_entry.bind('<Return>', self.on_parameter_change)

        # τ2 delay (for 3-pulse)
        self.tau2_label = ttk.Label(frame, text="Second delay (τ2):")
        self.tau2_scale = ttk.Scale(frame, from_=0.1, to=20.0, variable=self.tau2,
                                   orient=tk.HORIZONTAL, length=200, command=self._create_formatted_callback(self.tau2, self.on_parameter_change))
        self.tau2_entry = ttk.Entry(frame, textvariable=self.tau2, width=8)
        self.tau2_entry.bind('<Return>', self.on_parameter_change)

        # Time points
        ttk.Label(frame, text="Time points:").grid(row=6, column=0, sticky=tk.W)
        points_scale = ttk.Scale(frame, from_=100, to=2000, variable=self.points,
                                orient=tk.HORIZONTAL, length=200, command=self._create_formatted_callback(self.points, self.on_parameter_change))
        points_scale.grid(row=6, column=1, sticky=tk.EW, padx=5)
        points_entry = ttk.Entry(frame, textvariable=self.points, width=8)
        points_entry.grid(row=6, column=2)
        points_entry.bind('<Return>', self.on_parameter_change)

        # Detuning points
        ttk.Label(frame, text="Detuning points:").grid(row=7, column=0, sticky=tk.W)
        det_points_scale = ttk.Scale(frame, from_=51, to=501, variable=self.detuning_points,
                                    orient=tk.HORIZONTAL, length=200, command=self._create_formatted_callback(self.detuning_points, self.on_parameter_change))
        det_points_scale.grid(row=7, column=1, sticky=tk.EW, padx=5)
        det_points_entry = ttk.Entry(frame, textvariable=self.detuning_points, width=8)
        det_points_entry.grid(row=7, column=2)
        det_points_entry.bind('<Return>', self.on_parameter_change)

        frame.columnconfigure(1, weight=1)

        # Initialize visibility
        self.update_sequence_controls()

    def create_pulse_controls(self, parent):
        """Create pulse parameter controls"""
        frame = ttk.LabelFrame(parent, text="Pulse Parameters", padding=10)
        frame.pack(fill=tk.X, pady=(0, 5))

        # Pulse type
        ttk.Label(frame, text="Pulse type:").grid(row=0, column=0, sticky=tk.W)
        pulse_combo = ttk.Combobox(frame, textvariable=self.pulse_type,
                                  values=["hard", "soft"], width=15)
        pulse_combo.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5)
        pulse_combo.bind('<<ComboboxSelected>>', self.on_parameter_change)

        # Microwave field amplitude h1
        ttk.Label(frame, text="MW field amplitude (h1):").grid(row=1, column=0, sticky=tk.W)
        h1_scale = ttk.Scale(frame, from_=0.1, to=3.0, variable=self.h1,
                            orient=tk.HORIZONTAL, length=150, command=self._create_formatted_callback(self.h1, self.on_parameter_change))
        h1_scale.grid(row=1, column=1, sticky=tk.EW, padx=5)
        h1_entry = ttk.Entry(frame, textvariable=self.h1, width=8)
        h1_entry.grid(row=1, column=2)
        h1_entry.bind('<Return>', self.on_parameter_change)

        # Info label for h1
        h1_info = ttk.Label(frame, text="(1.0 = perfect pulses)",
                           font=('TkDefaultFont', 8), foreground='gray')
        h1_info.grid(row=2, column=0, columnspan=3, sticky=tk.W)

        # Phase controls frame
        phase_frame = ttk.Frame(frame)
        phase_frame.grid(row=3, column=0, columnspan=3, sticky=tk.EW, pady=5)
        phase_frame.columnconfigure(0, weight=1)

        # 2-pulse phases
        self.phase_2pulse_frame = ttk.LabelFrame(phase_frame, text="2-Pulse Phases", padding=5)

        # π/2 pulse phase
        ttk.Label(self.phase_2pulse_frame, text="π/2 pulse phase (°):").grid(row=0, column=0, sticky=tk.W)
        phase_pi2_scale = ttk.Scale(self.phase_2pulse_frame, from_=0, to=360, variable=self.phase_pi2,
                                   orient=tk.HORIZONTAL, length=120, command=self._create_formatted_callback(self.phase_pi2, self.on_parameter_change))
        phase_pi2_scale.grid(row=0, column=1, sticky=tk.EW, padx=2)
        phase_pi2_entry = ttk.Entry(self.phase_2pulse_frame, textvariable=self.phase_pi2, width=6)
        phase_pi2_entry.grid(row=0, column=2, padx=2)
        phase_pi2_entry.bind('<Return>', self.on_parameter_change)

        # π pulse phase
        ttk.Label(self.phase_2pulse_frame, text="π pulse phase (°):").grid(row=1, column=0, sticky=tk.W)
        phase_pi_scale = ttk.Scale(self.phase_2pulse_frame, from_=0, to=360, variable=self.phase_pi,
                                  orient=tk.HORIZONTAL, length=120, command=self._create_formatted_callback(self.phase_pi, self.on_parameter_change))
        phase_pi_scale.grid(row=1, column=1, sticky=tk.EW, padx=2)
        phase_pi_entry = ttk.Entry(self.phase_2pulse_frame, textvariable=self.phase_pi, width=6)
        phase_pi_entry.grid(row=1, column=2, padx=2)
        phase_pi_entry.bind('<Return>', self.on_parameter_change)

        self.phase_2pulse_frame.columnconfigure(1, weight=1)

        # 3-pulse phases
        self.phase_3pulse_frame = ttk.LabelFrame(phase_frame, text="3-Pulse Phases", padding=5)

        # First π/2 pulse phase
        ttk.Label(self.phase_3pulse_frame, text="1st π/2 phase (°):").grid(row=0, column=0, sticky=tk.W)
        phase_pi2_1_scale = ttk.Scale(self.phase_3pulse_frame, from_=0, to=360, variable=self.phase_pi2_1,
                                     orient=tk.HORIZONTAL, length=120, command=self._create_formatted_callback(self.phase_pi2_1, self.on_parameter_change))
        phase_pi2_1_scale.grid(row=0, column=1, sticky=tk.EW, padx=2)
        phase_pi2_1_entry = ttk.Entry(self.phase_3pulse_frame, textvariable=self.phase_pi2_1, width=6)
        phase_pi2_1_entry.grid(row=0, column=2, padx=2)
        phase_pi2_1_entry.bind('<Return>', self.on_parameter_change)

        # Second π/2 pulse phase
        ttk.Label(self.phase_3pulse_frame, text="2nd π/2 phase (°):").grid(row=1, column=0, sticky=tk.W)
        phase_pi2_2_scale = ttk.Scale(self.phase_3pulse_frame, from_=0, to=360, variable=self.phase_pi2_2,
                                     orient=tk.HORIZONTAL, length=120, command=self._create_formatted_callback(self.phase_pi2_2, self.on_parameter_change))
        phase_pi2_2_scale.grid(row=1, column=1, sticky=tk.EW, padx=2)
        phase_pi2_2_entry = ttk.Entry(self.phase_3pulse_frame, textvariable=self.phase_pi2_2, width=6)
        phase_pi2_2_entry.grid(row=1, column=2, padx=2)
        phase_pi2_2_entry.bind('<Return>', self.on_parameter_change)

        # Third π/2 pulse phase
        ttk.Label(self.phase_3pulse_frame, text="3rd π/2 phase (°):").grid(row=2, column=0, sticky=tk.W)
        phase_pi2_3_scale = ttk.Scale(self.phase_3pulse_frame, from_=0, to=360, variable=self.phase_pi2_3,
                                     orient=tk.HORIZONTAL, length=120, command=self._create_formatted_callback(self.phase_pi2_3, self.on_parameter_change))
        phase_pi2_3_scale.grid(row=2, column=1, sticky=tk.EW, padx=2)
        phase_pi2_3_entry = ttk.Entry(self.phase_3pulse_frame, textvariable=self.phase_pi2_3, width=6)
        phase_pi2_3_entry.grid(row=2, column=2, padx=2)
        phase_pi2_3_entry.bind('<Return>', self.on_parameter_change)

        self.phase_3pulse_frame.columnconfigure(1, weight=1)

        # Phase info
        phase_info = ttk.Label(phase_frame, text="(0°=+x, 90°=+y, 180°=-x, 270°=-y)",
                              font=('TkDefaultFont', 8), foreground='gray')
        phase_info.grid(row=1, column=0, columnspan=3, sticky=tk.W, pady=2)

        # Custom pulse duration
        duration_check = ttk.Checkbutton(frame, text="Custom pulse duration:",
                                        variable=self.use_custom_duration,
                                        command=self.on_parameter_change)
        duration_check.grid(row=4, column=0, columnspan=2, sticky=tk.W)

        duration_scale = ttk.Scale(frame, from_=0.1, to=10.0, variable=self.pulse_duration,
                                  orient=tk.HORIZONTAL, length=150, command=self._create_formatted_callback(self.pulse_duration, self.on_parameter_change))
        duration_scale.grid(row=5, column=0, columnspan=2, sticky=tk.EW, padx=5)
        duration_entry = ttk.Entry(frame, textvariable=self.pulse_duration, width=8)
        duration_entry.grid(row=5, column=2)
        duration_entry.bind('<Return>', self.on_parameter_change)

        frame.columnconfigure(1, weight=1)

        # Initialize phase control visibility
        self.update_phase_controls()

    def create_distribution_controls(self, parent):
        """Create distribution parameter controls"""
        frame = ttk.LabelFrame(parent, text="Spin Distribution", padding=10)
        frame.pack(fill=tk.X, pady=(0, 5))

        # Distribution type
        ttk.Label(frame, text="Type:").grid(row=0, column=0, sticky=tk.W)
        distri_combo = ttk.Combobox(frame, textvariable=self.distri_type,
                                   values=["gaussian", "lorentzian", "exponential", "uniform"],
                                   width=15)
        distri_combo.grid(row=0, column=1, columnspan=2, sticky=tk.EW, padx=5)
        distri_combo.bind('<<ComboboxSelected>>', self.on_parameter_change)

        # Linewidth
        ttk.Label(frame, text="Linewidth:").grid(row=1, column=0, sticky=tk.W)
        lw_scale = ttk.Scale(frame, from_=0.1, to=10.0, variable=self.linewidth,
                            orient=tk.HORIZONTAL, length=150, command=self._create_formatted_callback(self.linewidth, self.on_parameter_change))
        lw_scale.grid(row=1, column=1, sticky=tk.EW, padx=5)
        lw_entry = ttk.Entry(frame, textvariable=self.linewidth, width=8)
        lw_entry.grid(row=1, column=2)
        lw_entry.bind('<Return>', self.on_parameter_change)

        # Detuning range
        ttk.Label(frame, text="Detuning range:").grid(row=2, column=0, sticky=tk.W)
        ttk.Label(frame, text="Min:").grid(row=3, column=0, sticky=tk.W)
        min_entry = ttk.Entry(frame, textvariable=self.detuning_min, width=8)
        min_entry.grid(row=3, column=1, padx=5)
        min_entry.bind('<Return>', self.on_parameter_change)

        ttk.Label(frame, text="Max:").grid(row=3, column=2, sticky=tk.W)
        max_entry = ttk.Entry(frame, textvariable=self.detuning_max, width=8)
        max_entry.grid(row=3, column=3, padx=5)
        max_entry.bind('<Return>', self.on_parameter_change)

        frame.columnconfigure(1, weight=1)

    def create_display_controls(self, parent):
        """Create display option controls"""
        frame = ttk.LabelFrame(parent, text="Display Options", padding=10)
        frame.pack(fill=tk.X, pady=(0, 5))

        # Signal components
        ttk.Checkbutton(frame, text="Magnetization Sx", variable=self.show_sx,
                       command=self.on_display_change).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(frame, text="Magnetization Sy", variable=self.show_sy,
                       command=self.on_display_change).grid(row=0, column=1, sticky=tk.W)
        ttk.Checkbutton(frame, text="Magnitude |S|", variable=self.show_abs,
                       command=self.on_display_change).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(frame, text="Auto update", variable=self.auto_update
                       ).grid(row=1, column=1, sticky=tk.W)

        # Autoscale option
        autoscale_check = ttk.Checkbutton(frame, text="Auto scale axes", variable=self.auto_scale,
                                         command=self.on_display_change)
        autoscale_check.grid(row=2, column=0, columnspan=2, sticky=tk.W)

        # Manual axis limits (only enabled when autoscale is off)
        limits_frame = ttk.Frame(frame)
        limits_frame.grid(row=3, column=0, columnspan=2, sticky=tk.EW, pady=5)

        # X-axis limits
        ttk.Label(limits_frame, text="X-axis:").grid(row=0, column=0, sticky=tk.W)
        ttk.Label(limits_frame, text="Min:").grid(row=0, column=1, sticky=tk.W, padx=(10,0))
        x_min_entry = ttk.Entry(limits_frame, textvariable=self.x_min, width=8)
        x_min_entry.grid(row=0, column=2, padx=2)
        x_min_entry.bind('<Return>', self.on_display_change)

        ttk.Label(limits_frame, text="Max:").grid(row=0, column=3, sticky=tk.W, padx=(5,0))
        x_max_entry = ttk.Entry(limits_frame, textvariable=self.x_max, width=8)
        x_max_entry.grid(row=0, column=4, padx=2)
        x_max_entry.bind('<Return>', self.on_display_change)

        # Y-axis limits
        ttk.Label(limits_frame, text="Y-axis:").grid(row=1, column=0, sticky=tk.W)
        ttk.Label(limits_frame, text="Min:").grid(row=1, column=1, sticky=tk.W, padx=(10,0))
        y_min_entry = ttk.Entry(limits_frame, textvariable=self.y_min, width=8)
        y_min_entry.grid(row=1, column=2, padx=2)
        y_min_entry.bind('<Return>', self.on_display_change)

        ttk.Label(limits_frame, text="Max:").grid(row=1, column=3, sticky=tk.W, padx=(5,0))
        y_max_entry = ttk.Entry(limits_frame, textvariable=self.y_max, width=8)
        y_max_entry.grid(row=1, column=4, padx=2)
        y_max_entry.bind('<Return>', self.on_display_change)

        # Store entry widgets to enable/disable them
        self.axis_entries = [x_min_entry, x_max_entry, y_min_entry, y_max_entry]

        # Auto-fit button
        fit_button = ttk.Button(limits_frame, text="Fit to Data", command=self.fit_axes_to_data)
        fit_button.grid(row=2, column=0, columnspan=2, pady=5, sticky=tk.W)

        # Update entry states initially
        self.update_axis_entries_state()

    def create_action_buttons(self, parent):
        """Create action buttons"""
        frame = ttk.LabelFrame(parent, text="Actions", padding=10)
        frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Button(frame, text="Calculate", command=self.calculate_and_plot
                  ).grid(row=0, column=0, padx=5, pady=2, sticky=tk.EW)
        ttk.Button(frame, text="Reset", command=self.reset_parameters
                  ).grid(row=0, column=1, padx=5, pady=2, sticky=tk.EW)

        ttk.Button(frame, text="Save Plot", command=self.save_plot
                  ).grid(row=1, column=0, padx=5, pady=2, sticky=tk.EW)
        ttk.Button(frame, text="Export Data", command=self.export_data
                  ).grid(row=1, column=1, padx=5, pady=2, sticky=tk.EW)

        # Status label
        self.status_label = ttk.Label(frame, text="Ready", foreground="green")
        self.status_label.grid(row=2, column=0, columnspan=2, pady=5)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

    def create_plot(self, parent):
        """Create matplotlib plot"""
        self.fig, self.ax = plt.subplots(figsize=(10, 6))
        self.ax.set_xlabel('Time')
        self.ax.set_ylabel('Signal Amplitude')
        self.ax.set_title('2-Pulse Spin Echo Simulation')
        self.ax.grid(True, alpha=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Navigation toolbar
        toolbar = NavigationToolbar2Tk(self.canvas, parent)
        toolbar.update()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Store for current data
        self.current_time = None
        self.current_signal_x = None
        self.current_signal_y = None

    def on_parameter_change(self, event=None):
        """Handle parameter changes"""
        if self.auto_update.get() and not self.calculation_running:
            # Small delay to avoid too frequent updates
            self.root.after(100, self.calculate_and_plot)

    def update_axis_entries_state(self):
        """Enable/disable axis limit entries based on autoscale setting"""
        state = 'disabled' if self.auto_scale.get() else 'normal'
        for entry in self.axis_entries:
            entry.config(state=state)

    def on_sequence_change(self, event=None):
        """Handle sequence type change"""
        self.update_sequence_controls()
        self.update_phase_controls()
        self.update_plot_title()
        if self.auto_update.get() and not self.calculation_running:
            self.root.after(100, self.calculate_and_plot)

    def update_sequence_controls(self):
        """Show/hide controls based on sequence type"""
        if self.sequence_type.get() == "2pulse":
            # Show 2-pulse controls
            self.tau_label.grid(row=3, column=0, sticky=tk.W)
            self.tau_scale.grid(row=3, column=1, sticky=tk.EW, padx=5)
            self.tau_entry.grid(row=3, column=2)

            # Hide 3-pulse controls
            self.tau1_label.grid_remove()
            self.tau1_scale.grid_remove()
            self.tau1_entry.grid_remove()
            self.tau2_label.grid_remove()
            self.tau2_scale.grid_remove()
            self.tau2_entry.grid_remove()
        else:  # 3pulse
            # Hide 2-pulse controls
            self.tau_label.grid_remove()
            self.tau_scale.grid_remove()
            self.tau_entry.grid_remove()

            # Show 3-pulse controls
            self.tau1_label.grid(row=3, column=0, sticky=tk.W)
            self.tau1_scale.grid(row=3, column=1, sticky=tk.EW, padx=5)
            self.tau1_entry.grid(row=3, column=2)
            self.tau2_label.grid(row=4, column=0, sticky=tk.W)
            self.tau2_scale.grid(row=4, column=1, sticky=tk.EW, padx=5)
            self.tau2_entry.grid(row=4, column=2)

    def update_phase_controls(self):
        """Show/hide phase controls based on sequence type"""
        if self.sequence_type.get() == "2pulse":
            self.phase_2pulse_frame.grid(row=0, column=0, sticky=tk.EW, pady=2)
            self.phase_3pulse_frame.grid_forget()
        else:  # 3pulse
            self.phase_2pulse_frame.grid_forget()
            self.phase_3pulse_frame.grid(row=0, column=0, sticky=tk.EW, pady=2)

    def update_plot_title(self):
        """Update plot title based on sequence type"""
        if hasattr(self, 'ax'):
            if self.sequence_type.get() == "2pulse":
                self.ax.set_title('2-Pulse Spin Echo Simulation (Single Core)', fontsize=10, fontweight='bold')
            else:
                self.ax.set_title('3-Pulse Stimulated Echo Simulation (Single Core)', fontsize=10, fontweight='bold')
            if hasattr(self, 'canvas'):
                self.canvas.draw()

    def fit_axes_to_data(self):
        """Fit axes to current data and disable autoscale"""
        if (self.current_time is not None and
            self.current_signal_x is not None and
            self.current_signal_y is not None):

            # Get data bounds
            x_data_min = np.min(self.current_time)
            x_data_max = np.max(self.current_time)

            # Collect all y data that's currently displayed
            y_data = []
            if self.show_sx.get():
                y_data.extend(self.current_signal_x)
            if self.show_sy.get():
                y_data.extend(self.current_signal_y)
            if self.show_abs.get():
                signal_abs = np.sqrt(self.current_signal_x**2 + self.current_signal_y**2)
                y_data.extend(signal_abs)

            if y_data:
                y_data_min = np.min(y_data)
                y_data_max = np.max(y_data)

                # Add 5% margin
                x_margin = (x_data_max - x_data_min) * 0.05
                y_margin = (y_data_max - y_data_min) * 0.05

                self.x_min.set(x_data_min - x_margin)
                self.x_max.set(x_data_max + x_margin)
                self.y_min.set(y_data_min - y_margin)
                self.y_max.set(y_data_max + y_margin)

                # Disable autoscale and update plot
                self.auto_scale.set(False)
                self.update_axis_entries_state()
                self.update_plot()

    def on_display_change(self):
        """Handle display option changes"""
        self.update_axis_entries_state()
        if (self.current_time is not None and
            self.current_signal_x is not None and
            self.current_signal_y is not None):
            self.update_plot()

    def calculate_and_plot(self):
        """Calculate and plot in separate thread"""
        if self.calculation_running:
            return

        self.calculation_running = True
        self.calculation_start_time = time.time()
        self.status_label.config(text="Calculating...", foreground="orange")
        self.root.update()

        # Run calculation in thread to keep GUI responsive
        thread = threading.Thread(target=self._calculate_worker)
        thread.daemon = True
        thread.start()

    def _calculate_worker(self):
        """Worker thread for calculation"""
        try:
            # Get parameters
            params = self.get_current_parameters()

            # Generate detuning values
            detuning_values = np.linspace(params['detuning_min'], params['detuning_max'],
                                         params['detuning_points'])

            # Calculate distribution weights
            distri_weights = spin_distribution(detuning_values, params['linewidth'],
                                             params['distri_type'])
            distri_weights = distri_weights / np.sum(distri_weights)

            if self.sequence_type.get() == "2pulse":
                # Single core calculation for 2-pulse
                signals = []
                total_points = len(detuning_values)
                for i, delta in enumerate(detuning_values):
                    # Update progress
                    progress = (i + 1) / total_points * 100
                    self.root.after(0, self._update_progress, f"Calculating... {progress:.0f}% ({i+1}/{total_points})")

                    signal = two_pulse_hahn(
                        delta, params['dt'], params['tp'], params['tau'],
                        params['points'], params['pulse_type'],
                        params['pulse_duration'] if params['use_custom_duration'] else None,
                        params['h1'],  # Add h1 parameter
                        params['phase_pi2'],  # Add π/2 phase
                        params['phase_pi']    # Add π phase
                    )
                    signals.append(signal)
            else:  # 3pulse
                # Single core calculation for 3-pulse
                signals = []
                total_points = len(detuning_values)
                for i, delta in enumerate(detuning_values):
                    # Update progress
                    progress = (i + 1) / total_points * 100
                    self.root.after(0, self._update_progress, f"Calculating... {progress:.0f}% ({i+1}/{total_points})")

                    signal = three_pulse_sequence(
                        delta, params['dt'], params['tp'], params['tau1'], params['tau2'],
                        params['points'], params['pulse_type'],
                        params['pulse_duration'] if params['use_custom_duration'] else None,
                        params['h1'],  # Add h1 parameter
                        params['phase_pi2_1'],  # First π/2 phase
                        params['phase_pi2_2'],  # Second π/2 phase
                        params['phase_pi2_3']   # Third π/2 phase
                    )
                    signals.append(signal)

            # Separate x and y components
            signals_x = np.array([sig[0] for sig in signals])  # Sx components
            signals_y = np.array([sig[1] for sig in signals])  # Sy components

            # Apply distribution weighting
            weighted_signals_x = signals_x.T * distri_weights
            weighted_signals_y = signals_y.T * distri_weights

            total_signal_x = np.sum(weighted_signals_x, axis=1)
            total_signal_y = np.sum(weighted_signals_y, axis=1)

            # Generate time axis
            time_axis = params['dt'] * np.arange(params['points'])

            # Update GUI in main thread
            self.root.after(0, self._update_results, time_axis, total_signal_x, total_signal_y)

        except Exception as e:
            self.root.after(0, self._handle_error, str(e))

    def _update_progress(self, progress_text):
        """Update progress indicator in main thread"""
        self.status_label.config(text=progress_text, foreground="orange")

    def _update_results(self, time_axis, signal_x, signal_y):
        """Update results in main thread"""
        self.current_time = time_axis
        self.current_signal_x = signal_x
        self.current_signal_y = signal_y
        self.update_plot()

        # Calculate and display execution time
        calculation_time = time.time() - self.calculation_start_time
        self.status_label.config(text=f"Calculation completed in {calculation_time:.2f}s", foreground="green")
        self.calculation_running = False

    def _handle_error(self, error_msg):
        """Handle calculation error"""
        self.status_label.config(text=f"Error: {error_msg}", foreground="red")
        self.calculation_running = False
        messagebox.showerror("Calculation Error", error_msg)

    def update_plot(self):
        """Update the plot with current data"""
        if (self.current_time is None or
            self.current_signal_x is None or
            self.current_signal_y is None):
            return

        # Import Set1 colormap from matplotlib
        from matplotlib.colors import to_rgba
        import matplotlib.cm as cm

        # Get Set1 colors
        set1_colors = plt.cm.Set1.colors
        color_sx = set1_colors[0]  # Red
        color_sy = set1_colors[1]  # Blue
        color_abs = set1_colors[2] # Green

        self.ax.clear()

        # Plot selected components
        lines_plotted = 0

        if self.show_sx.get():
            self.ax.plot(self.current_time, self.current_signal_x,
                        color=color_sx, linewidth=1.2, label='⟨Sx⟩', alpha=0.8)
            lines_plotted += 1

        if self.show_sy.get():
            self.ax.plot(self.current_time, self.current_signal_y,
                        color=color_sy, linewidth=1.2, label='⟨Sy⟩', alpha=0.8)
            lines_plotted += 1

        if self.show_abs.get():
            signal_abs = np.sqrt(self.current_signal_x**2 + self.current_signal_y**2)
            self.ax.plot(self.current_time, signal_abs,
                        color=color_abs, linewidth=1.2, label='|⟨S⟩|', alpha=0.8)
            lines_plotted += 1

        # If nothing selected, show Sx by default
        if lines_plotted == 0:
            self.ax.plot(self.current_time, self.current_signal_x,
                        color=color_sx, linewidth=1.2, label='⟨Sx⟩', alpha=0.8)
            lines_plotted = 1

        self.ax.set_xlabel('Time', fontsize=9)
        self.ax.set_ylabel('Magnetization', fontsize=9)

        # Set title based on sequence type
        if self.sequence_type.get() == "2pulse":
            self.ax.set_title('2-Pulse Spin Echo Simulation (Single Core)', fontsize=10, fontweight='bold')
        else:
            self.ax.set_title('3-Pulse Stimulated Echo Simulation (Single Core)', fontsize=10, fontweight='bold')

        self.ax.grid(True, alpha=0.3)

        # Set axis limits based on autoscale setting
        if not self.auto_scale.get():
            self.ax.set_xlim(self.x_min.get(), self.x_max.get())
            self.ax.set_ylim(self.y_min.get(), self.y_max.get())

        if lines_plotted > 1:
            self.ax.legend(fontsize=8)

        self.canvas.draw()

    def get_current_parameters(self):
        """Get current parameter values"""
        params = {
            'dt': self.dt.get(),
            'tp': self.tp.get(),
            'points': self.points.get(),
            'detuning_points': self.detuning_points.get(),
            'linewidth': self.linewidth.get(),
            'detuning_min': self.detuning_min.get(),
            'detuning_max': self.detuning_max.get(),
            'pulse_type': self.pulse_type.get(),
            'pulse_duration': self.pulse_duration.get(),
            'use_custom_duration': self.use_custom_duration.get(),
            'distri_type': self.distri_type.get(),
            'h1': self.h1.get()
        }

        # Add sequence-specific parameters
        if self.sequence_type.get() == "2pulse":
            params.update({
                'tau': self.tau.get(),
                'phase_pi2': np.deg2rad(self.phase_pi2.get()),
                'phase_pi': np.deg2rad(self.phase_pi.get())
            })
        else:  # 3pulse
            params.update({
                'tau1': self.tau1.get(),
                'tau2': self.tau2.get(),
                'phase_pi2_1': np.deg2rad(self.phase_pi2_1.get()),
                'phase_pi2_2': np.deg2rad(self.phase_pi2_2.get()),
                'phase_pi2_3': np.deg2rad(self.phase_pi2_3.get())
            })

        return params

    def reset_parameters(self):
        """Reset all parameters to defaults"""
        self.dt.set(0.01)
        self.tp.set(1.0)
        self.tau.set(5.0)
        self.tau1.set(3.0)
        self.tau2.set(8.0)
        self.points.set(800)
        self.detuning_points.set(101)
        self.linewidth.set(2.0)
        self.detuning_min.set(-10.0)
        self.detuning_max.set(10.0)
        self.sequence_type.set("2pulse")
        self.pulse_type.set("hard")
        self.pulse_duration.set(2.0)
        self.use_custom_duration.set(False)
        self.h1.set(1.0)

        # Reset 2-pulse phases
        self.phase_pi2.set(0.0)
        self.phase_pi.set(0.0)

        # Reset 3-pulse phases
        self.phase_pi2_1.set(0.0)
        self.phase_pi2_2.set(90.0)
        self.phase_pi2_3.set(0.0)

        self.distri_type.set("gaussian")
        self.show_sx.set(True)
        self.show_sy.set(True)
        self.show_abs.set(False)
        self.auto_scale.set(True)
        self.x_min.set(0.0)
        self.x_max.set(20.0)
        self.y_min.set(-1.0)
        self.y_max.set(1.0)

        # Update controls visibility
        self.update_sequence_controls()
        self.update_phase_controls()
        self.update_axis_entries_state()

        if self.auto_update.get():
            self.calculate_and_plot()

    def save_plot(self):
        """Save current plot"""
        if (self.current_time is not None and
            self.current_signal_x is not None and
            self.current_signal_y is not None):
            filename = tk.filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf"),
                          ("SVG files", "*.svg"), ("All files", "*.*")]
            )
            if filename:
                self.fig.savefig(filename, dpi=300, bbox_inches='tight')
                messagebox.showinfo("Success", f"Plot saved: {filename}")

    def export_data(self):
        """Export current data to CSV"""
        if (self.current_time is not None and
            self.current_signal_x is not None and
            self.current_signal_y is not None):
            filename = tk.filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            if filename:
                signal_abs = np.sqrt(self.current_signal_x**2 + self.current_signal_y**2)
                data = np.column_stack([
                    self.current_time,
                    self.current_signal_x,
                    self.current_signal_y,
                    signal_abs
                ])
                np.savetxt(filename, data, delimiter=',',
                          header='Time,Sx,Sy,Magnitude', comments='')
                messagebox.showinfo("Success", f"Data exported: {filename}")

def main():
    root = tk.Tk()
    app = SpinEchoGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()