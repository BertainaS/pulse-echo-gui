#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tkinter GUI for Interactive Pulse Exploration

Complete GUI interface for exploring shaped pulse effects with real-time
parameter modification and visualization.

@author: sylvainbertaina
"""

import queue
import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from pulseseq import ShapedPulseSequence, ShapedSpinEchoSimulator, plot_pulse_shape
from tkinter import messagebox, ttk


class PulseExplorerGUI:
    """Main GUI class for pulse exploration."""

    def __init__(self, root):
        self.root = root
        self.root.title("Shaped Pulse Explorer")
        self.root.geometry("1400x900")

        # Parameters
        self.params = {
            "tau": tk.DoubleVar(value=5.0),
            "pulse_duration": tk.DoubleVar(value=1.5),
            "sx_amplitude": tk.DoubleVar(value=1.0),
            "sy_amplitude": tk.DoubleVar(value=0.0),
            "linewidth": tk.DoubleVar(value=2.0),
            "detection_points": tk.IntVar(value=600),
            "dt": tk.DoubleVar(value=0.02),
            "detuning_points": tk.IntVar(value=51),
            "pulse_shape": tk.StringVar(value="gaussian"),
            "n_jobs": tk.IntVar(value=1),
        }

        # Pulse shape specific parameters
        self.shape_params = {
            "gaussian": {"sigma_factor": tk.DoubleVar(value=4.0)},
            "square": {"rise_time": tk.DoubleVar(value=0.0)},
            "sech": {"beta": tk.DoubleVar(value=5.0)},
            "wurst": {
                "freq_start": tk.DoubleVar(value=-8.0),
                "freq_end": tk.DoubleVar(value=8.0),
                "wurst_n": tk.IntVar(value=40),
            },
            "chirp": {
                "freq_start": tk.DoubleVar(value=-6.0),
                "freq_end": tk.DoubleVar(value=6.0),
                "envelope": tk.StringVar(value="gaussian"),
            },
            "noisy": {
                "base_shape": tk.StringVar(value="gaussian"),
                "amp_noise": tk.DoubleVar(value=0.1),
                "phase_noise": tk.DoubleVar(value=0.05),
                "seed": tk.IntVar(value=42),
            },
        }

        # Simulation state
        self.simulator = ShapedSpinEchoSimulator(n_jobs=1)
        self.simulation_running = False
        self.result_queue = queue.Queue()
        self.auto_calculate = tk.BooleanVar(value=True)
        self.calculation_times = {"pulse_shape": 0.0, "echo": 0.0}

        # Collect all DoubleVar for formatting
        self._double_vars = []
        for key, var in self.params.items():
            if isinstance(var, tk.DoubleVar):
                self._double_vars.append(var)

        for shape, params_dict in self.shape_params.items():
            for key, var in params_dict.items():
                if isinstance(var, tk.DoubleVar):
                    self._double_vars.append(var)

        # Flag to prevent recursive formatting
        self._formatting_in_progress = False

        # Setup parameter change callbacks
        self.setup_parameter_callbacks()

        self.setup_gui()

        # Start periodic formatting (every 500ms)
        self._periodic_format()

    def _periodic_format(self):
        """Periodically format all variables to maintain 4-digit display"""
        self._format_all_variables()
        self.root.after(500, self._periodic_format)

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

    def create_editable_entry(
        self, parent, variable, row, column, format_str=":.4g", width=8
    ):
        """Create an editable entry that displays and allows editing of variable values."""

        def update_entry_from_variable(*args):
            try:
                value = variable.get()
                if format_str == ":.0f":
                    formatted_text = f"{value:.0f}"
                else:
                    formatted_text = f"{value:.4g}"
                if entry.get() != formatted_text:
                    entry.delete(0, tk.END)
                    entry.insert(0, formatted_text)
            except:
                pass

        def update_variable_from_entry(event=None):
            try:
                text_value = entry.get().strip()
                if text_value:
                    if isinstance(variable, tk.IntVar):
                        new_value = int(
                            float(text_value)
                        )  # Allow float input but convert to int
                    else:
                        new_value = float(text_value)

                    # Apply basic sanity checks but allow values beyond slider ranges
                    # Only prevent obviously invalid values
                    if hasattr(entry, "_param_name"):
                        param_name = entry._param_name
                        if param_name == "n_jobs" and new_value < 1:
                            new_value = 1  # n_jobs must be at least 1
                        elif (
                            param_name in ["detection_points", "detuning_points"]
                            and new_value < 10
                        ):
                            new_value = 10  # Need minimum points for simulation
                        elif param_name == "dt" and new_value <= 0:
                            new_value = 0.001  # Time step must be positive
                        elif (
                            param_name in ["pulse_duration", "tau", "linewidth"]
                            and new_value <= 0
                        ):
                            new_value = 0.1  # Durations must be positive
                        elif param_name.startswith("shape_"):
                            # Shape parameter validation
                            shape_param = param_name.replace("shape_", "")
                            if shape_param in ["wurst_n", "seed"] and new_value < 1:
                                new_value = 1  # These must be positive integers
                            elif (
                                shape_param in ["sigma_factor", "beta"]
                                and new_value <= 0
                            ):
                                new_value = 0.1  # These must be positive

                    variable.set(new_value)
            except ValueError:
                # Reset to current value if invalid input
                update_entry_from_variable()

        # Create entry widget
        entry = ttk.Entry(parent, width=width, justify=tk.CENTER)
        entry.grid(row=row, column=column, padx=5, pady=2)

        # Initialize with current value
        if format_str == ":.0f":
            initial_text = f"{variable.get():.0f}"
        else:
            initial_text = f"{variable.get():.4g}"
        entry.insert(0, initial_text)

        # Bind events
        entry.bind("<Return>", update_variable_from_entry)
        entry.bind("<FocusOut>", update_variable_from_entry)
        variable.trace("w", update_entry_from_variable)

        return entry

    def setup_parameter_callbacks(self):
        """Setup callbacks for automatic calculation when parameters change."""
        # Add callbacks to all main parameters
        for param_name, param_var in self.params.items():
            if param_name != "n_jobs":  # Don't trigger on n_jobs change
                param_var.trace("w", self.on_parameter_changed)

        # Add callbacks to shape parameters
        for shape_name, shape_params in self.shape_params.items():
            for param_name, param_var in shape_params.items():
                param_var.trace("w", self.on_parameter_changed)

    def on_parameter_changed(self, *args):
        """Called when any parameter changes."""
        if self.auto_calculate.get() and not self.simulation_running:
            # Schedule calculation with a small delay to avoid too frequent updates
            self.root.after(500, self.auto_calculate_pulse_and_echo)

    def auto_calculate_pulse_and_echo(self):
        """Automatically calculate both pulse shape and echo if enabled."""
        if self.auto_calculate.get() and not self.simulation_running:
            self.calculate_pulse_and_echo()

    def setup_gui(self):
        """Setup the GUI layout."""

        # Main frame
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel for controls
        control_frame = ttk.LabelFrame(main_frame, text="Parameters", padding=10)
        control_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Right panel for plots
        plot_frame = ttk.LabelFrame(main_frame, text="Visualization", padding=10)
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.setup_control_panel(control_frame)
        self.setup_plot_panel(plot_frame)

    def setup_control_panel(self, parent):
        """Setup the control panel with all parameters."""

        # Create notebook for organized parameters
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Basic Parameters Tab
        basic_frame = ttk.Frame(notebook)
        notebook.add(basic_frame, text="Basic Parameters")
        self.setup_basic_parameters(basic_frame)

        # Pulse Shape Tab
        shape_frame = ttk.Frame(notebook)
        notebook.add(shape_frame, text="Pulse Shape")
        self.setup_pulse_shape_parameters(shape_frame)

        # Multi-axis Tab
        multiaxis_frame = ttk.Frame(notebook)
        notebook.add(multiaxis_frame, text="Multi-axis")
        self.setup_multiaxis_parameters(multiaxis_frame)

        # Simulation Tab
        sim_frame = ttk.Frame(notebook)
        notebook.add(sim_frame, text="Simulation")
        self.setup_simulation_parameters(sim_frame)

        # Control buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=(10, 0))

        # Main calculation button
        ttk.Button(
            button_frame,
            text="Calculate Pulse & Echo",
            command=self.calculate_pulse_and_echo,
        ).pack(fill=tk.X, pady=2)

        # Separator
        ttk.Separator(button_frame, orient="horizontal").pack(fill=tk.X, pady=5)

        # Individual buttons
        ttk.Button(
            button_frame, text="Show Pulse Shape Only", command=self.show_pulse_shape
        ).pack(fill=tk.X, pady=2)
        ttk.Button(
            button_frame, text="Run Echo Simulation Only", command=self.run_simulation
        ).pack(fill=tk.X, pady=2)

        # Separator
        ttk.Separator(button_frame, orient="horizontal").pack(fill=tk.X, pady=5)

        # Auto-calculate checkbox
        ttk.Checkbutton(
            button_frame, text="Auto-calculate on change", variable=self.auto_calculate
        ).pack(fill=tk.X, pady=2)

        ttk.Button(
            button_frame, text="Reset to Defaults", command=self.reset_parameters
        ).pack(fill=tk.X, pady=2)

        # Quick access to n_jobs
        jobs_frame = ttk.LabelFrame(button_frame, text="Performance")
        jobs_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(jobs_frame, text="Parallel jobs:").pack(anchor=tk.W)
        jobs_control_frame = ttk.Frame(jobs_frame)
        jobs_control_frame.pack(fill=tk.X, padx=5)

        ttk.Scale(
            jobs_control_frame,
            from_=1,
            to=8,
            variable=self.params["n_jobs"],
            orient=tk.HORIZONTAL,
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Create a quick editable entry for n_jobs
        def update_quick_entry(*args):
            try:
                value = self.params["n_jobs"].get()
                if self.jobs_quick_entry.get() != f"{value:.0f}":
                    self.jobs_quick_entry.delete(0, tk.END)
                    self.jobs_quick_entry.insert(0, f"{value:.0f}")
            except:
                pass

        def update_from_quick_entry(event=None):
            try:
                value = int(float(self.jobs_quick_entry.get().strip()))
                value = max(1, value)  # Only ensure minimum of 1, no upper limit
                self.params["n_jobs"].set(value)
            except ValueError:
                update_quick_entry()

        self.jobs_quick_entry = ttk.Entry(
            jobs_control_frame, width=6, justify=tk.CENTER
        )
        self.jobs_quick_entry.pack(side=tk.RIGHT, padx=(5, 0))
        self.jobs_quick_entry.insert(0, "1")
        self.jobs_quick_entry.bind("<Return>", update_from_quick_entry)
        self.jobs_quick_entry.bind("<FocusOut>", update_from_quick_entry)
        self.params["n_jobs"].trace("w", update_quick_entry)

        # Timing display
        self.timing_frame = ttk.LabelFrame(button_frame, text="Calculation Times")
        self.timing_frame.pack(fill=tk.X, pady=(5, 0))

        self.pulse_time_label = ttk.Label(self.timing_frame, text="Pulse shape: -- s")
        self.pulse_time_label.pack(anchor=tk.W)

        self.echo_time_label = ttk.Label(
            self.timing_frame, text="Echo simulation: -- s"
        )
        self.echo_time_label.pack(anchor=tk.W)

    def setup_basic_parameters(self, parent):
        """Setup basic sequence parameters."""

        ttk.Label(parent, text="Echo delay (τ):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent,
            from_=1.0,
            to=10.0,
            variable=self.params["tau"],
            orient=tk.HORIZONTAL,
        ).grid(row=0, column=1, sticky=tk.EW, padx=5)
        entry1 = self.create_editable_entry(parent, self.params["tau"], 0, 2)
        entry1._param_name = "tau"

        ttk.Label(parent, text="Pulse duration:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent,
            from_=0.5,
            to=3.0,
            variable=self.params["pulse_duration"],
            orient=tk.HORIZONTAL,
        ).grid(row=1, column=1, sticky=tk.EW, padx=5)
        entry2 = self.create_editable_entry(parent, self.params["pulse_duration"], 1, 2)
        entry2._param_name = "pulse_duration"

        ttk.Label(parent, text="Linewidth:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Scale(
            parent,
            from_=0.5,
            to=5.0,
            variable=self.params["linewidth"],
            orient=tk.HORIZONTAL,
        ).grid(row=2, column=1, sticky=tk.EW, padx=5)
        entry3 = self.create_editable_entry(parent, self.params["linewidth"], 2, 2)
        entry3._param_name = "linewidth"

        ttk.Label(parent, text="Detection points:").grid(
            row=3, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent,
            from_=200,
            to=1000,
            variable=self.params["detection_points"],
            orient=tk.HORIZONTAL,
        ).grid(row=3, column=1, sticky=tk.EW, padx=5)
        entry4 = self.create_editable_entry(
            parent, self.params["detection_points"], 3, 2, ":.0f"
        )
        entry4._param_name = "detection_points"

        parent.grid_columnconfigure(1, weight=1)

    def setup_pulse_shape_parameters(self, parent):
        """Setup pulse shape selection and parameters."""

        # Pulse shape selection
        ttk.Label(parent, text="Pulse Shape:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        shape_combo = ttk.Combobox(
            parent,
            textvariable=self.params["pulse_shape"],
            values=["gaussian", "square", "sech", "wurst", "chirp", "noisy"],
            state="readonly",
        )
        shape_combo.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        shape_combo.bind("<<ComboboxSelected>>", self.on_pulse_shape_changed)

        # Shape-specific parameters frame
        self.shape_params_frame = ttk.LabelFrame(parent, text="Shape Parameters")
        self.shape_params_frame.grid(
            row=1, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

        self.update_shape_parameters()

        parent.grid_columnconfigure(1, weight=1)

    def setup_multiaxis_parameters(self, parent):
        """Setup multi-axis parameters."""

        ttk.Label(parent, text="Sx amplitude (Real):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent,
            from_=0.0,
            to=2.0,
            variable=self.params["sx_amplitude"],
            orient=tk.HORIZONTAL,
        ).grid(row=0, column=1, sticky=tk.EW, padx=5)
        entry_sx = self.create_editable_entry(parent, self.params["sx_amplitude"], 0, 2)
        entry_sx._param_name = "sx_amplitude"

        ttk.Label(parent, text="Sy amplitude (Imag):").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent,
            from_=0.0,
            to=2.0,
            variable=self.params["sy_amplitude"],
            orient=tk.HORIZONTAL,
        ).grid(row=1, column=1, sticky=tk.EW, padx=5)
        entry_sy = self.create_editable_entry(parent, self.params["sy_amplitude"], 1, 2)
        entry_sy._param_name = "sy_amplitude"

        # Quick presets
        preset_frame = ttk.LabelFrame(parent, text="Quick Presets")
        preset_frame.grid(row=2, column=0, columnspan=3, sticky=tk.EW, pady=10)

        ttk.Button(
            preset_frame,
            text="Pure Sx (1,0)",
            command=lambda: self.set_multiaxis(1.0, 0.0),
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            preset_frame,
            text="Pure Sy (0,1)",
            command=lambda: self.set_multiaxis(0.0, 1.0),
        ).pack(side=tk.LEFT, padx=2)
        ttk.Button(
            preset_frame,
            text="Equal (1,1)",
            command=lambda: self.set_multiaxis(1.0, 1.0),
        ).pack(side=tk.LEFT, padx=2)

        parent.grid_columnconfigure(1, weight=1)

    def setup_simulation_parameters(self, parent):
        """Setup simulation parameters."""

        ttk.Label(parent, text="Time step (dt):").grid(
            row=0, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent, from_=0.01, to=0.1, variable=self.params["dt"], orient=tk.HORIZONTAL
        ).grid(row=0, column=1, sticky=tk.EW, padx=5)
        entry_dt = self.create_editable_entry(parent, self.params["dt"], 0, 2)
        entry_dt._param_name = "dt"

        ttk.Label(parent, text="Detuning points:").grid(
            row=1, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent,
            from_=21,
            to=101,
            variable=self.params["detuning_points"],
            orient=tk.HORIZONTAL,
        ).grid(row=1, column=1, sticky=tk.EW, padx=5)
        entry_det = self.create_editable_entry(
            parent, self.params["detuning_points"], 1, 2, ":.0f"
        )
        entry_det._param_name = "detuning_points"

        ttk.Label(parent, text="Parallel jobs:").grid(
            row=2, column=0, sticky=tk.W, pady=2
        )
        ttk.Scale(
            parent, from_=1, to=8, variable=self.params["n_jobs"], orient=tk.HORIZONTAL
        ).grid(row=2, column=1, sticky=tk.EW, padx=5)
        entry_jobs = self.create_editable_entry(
            parent, self.params["n_jobs"], 2, 2, ":.0f"
        )
        entry_jobs._param_name = "n_jobs"

        parent.grid_columnconfigure(1, weight=1)

    def setup_plot_panel(self, parent):
        """Setup the plotting panel."""

        # Create matplotlib figure
        self.fig = Figure(figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, parent)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        # Status bar with more detailed info
        status_frame = ttk.Frame(parent)
        status_frame.pack(fill=tk.X, pady=(5, 0))

        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(
            status_frame, textvariable=self.status_var, relief=tk.SUNKEN
        )
        status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.jobs_var = tk.StringVar(value="Jobs: 1")
        jobs_label = ttk.Label(
            status_frame, textvariable=self.jobs_var, relief=tk.SUNKEN
        )
        jobs_label.pack(side=tk.RIGHT, padx=(5, 0))

    def on_pulse_shape_changed(self, event=None):
        """Handle pulse shape change."""
        self.update_shape_parameters()

    def update_shape_parameters(self):
        """Update shape-specific parameters display."""

        # Clear existing widgets
        for widget in self.shape_params_frame.winfo_children():
            widget.destroy()

        shape = self.params["pulse_shape"].get()
        params = self.shape_params[shape]

        row = 0
        for param_name, param_var in params.items():
            ttk.Label(self.shape_params_frame, text=f"{param_name}:").grid(
                row=row, column=0, sticky=tk.W, pady=2
            )

            if isinstance(param_var, tk.StringVar):
                if param_name == "envelope":
                    combo = ttk.Combobox(
                        self.shape_params_frame,
                        textvariable=param_var,
                        values=["gaussian", "square", "sech"],
                        state="readonly",
                    )
                    combo.grid(row=row, column=1, sticky=tk.EW, padx=5)
                elif param_name == "base_shape":
                    combo = ttk.Combobox(
                        self.shape_params_frame,
                        textvariable=param_var,
                        values=["gaussian", "square", "sech"],
                        state="readonly",
                    )
                    combo.grid(row=row, column=1, sticky=tk.EW, padx=5)
                else:
                    entry = ttk.Entry(self.shape_params_frame, textvariable=param_var)
                    entry.grid(row=row, column=1, sticky=tk.EW, padx=5)
            else:
                # Determine appropriate range for the parameter
                if "freq" in param_name:
                    from_val, to_val = -20.0, 20.0
                elif param_name == "wurst_n":
                    from_val, to_val = 10, 100
                elif param_name == "seed":
                    from_val, to_val = 1, 100
                elif "noise" in param_name:
                    from_val, to_val = 0.0, 0.5
                elif param_name == "beta":
                    from_val, to_val = 1.0, 20.0
                elif param_name == "sigma_factor":
                    from_val, to_val = 1.0, 10.0
                else:
                    from_val, to_val = 0.1, 10.0

                scale = ttk.Scale(
                    self.shape_params_frame,
                    from_=from_val,
                    to=to_val,
                    variable=param_var,
                    orient=tk.HORIZONTAL,
                )
                scale.grid(row=row, column=1, sticky=tk.EW, padx=5)

            # Create editable entry for shape parameters
            if isinstance(param_var, tk.IntVar):
                entry = self.create_editable_entry(
                    self.shape_params_frame, param_var, row, 2, ":.0f"
                )
            else:
                entry = self.create_editable_entry(
                    self.shape_params_frame, param_var, row, 2
                )

            # Store parameter name for validation
            entry._param_name = f"shape_{param_name}"

            row += 1

        self.shape_params_frame.grid_columnconfigure(1, weight=1)

    def set_multiaxis(self, sx, sy):
        """Set multiaxis values."""
        self.params["sx_amplitude"].set(sx)
        self.params["sy_amplitude"].set(sy)

    def reset_parameters(self):
        """Reset all parameters to defaults."""
        self.params["tau"].set(5.0)
        self.params["pulse_duration"].set(1.5)
        self.params["sx_amplitude"].set(1.0)
        self.params["sy_amplitude"].set(0.0)
        self.params["linewidth"].set(2.0)
        self.params["detection_points"].set(600)
        self.params["dt"].set(0.02)
        self.params["detuning_points"].set(51)
        self.params["pulse_shape"].set("gaussian")
        self.params["n_jobs"].set(1)

        # Reset shape parameters
        for shape_params in self.shape_params.values():
            for param_name, param_var in shape_params.items():
                if param_name == "sigma_factor":
                    param_var.set(4.0)
                elif param_name == "rise_time":
                    param_var.set(0.0)
                elif param_name == "beta":
                    param_var.set(5.0)
                elif param_name == "freq_start":
                    param_var.set(-8.0 if "wurst" in str(param_var) else -6.0)
                elif param_name == "freq_end":
                    param_var.set(8.0 if "wurst" in str(param_var) else 6.0)
                elif param_name == "wurst_n":
                    param_var.set(40)
                elif param_name == "envelope":
                    param_var.set("gaussian")
                elif param_name == "base_shape":
                    param_var.set("gaussian")
                elif param_name == "amp_noise":
                    param_var.set(0.1)
                elif param_name == "phase_noise":
                    param_var.set(0.05)
                elif param_name == "seed":
                    param_var.set(42)

        self.update_shape_parameters()

    def get_current_shape_params(self):
        """Get current shape parameters as dictionary."""
        shape = self.params["pulse_shape"].get()
        params = {}
        for param_name, param_var in self.shape_params[shape].items():
            params[param_name] = param_var.get()
        return params

    def calculate_pulse_and_echo(self):
        """Calculate both pulse shape and echo simulation with timing."""
        if self.simulation_running:
            messagebox.showwarning("Warning", "Calculation already running!")
            return

        self.simulation_running = True

        # Update n_jobs in simulator
        self.simulator.n_jobs = self.params["n_jobs"].get()
        self.jobs_var.set(f"Jobs: {self.params['n_jobs'].get()}")

        self.status_var.set("Calculating pulse shape and echo...")

        # Run calculation in separate thread
        threading.Thread(target=self._combined_calculation_thread, daemon=True).start()

        # Check for results
        self.root.after(100, self._check_combined_results)

    def _combined_calculation_thread(self):
        """Run combined calculation in separate thread."""
        try:
            start_total = time.time()

            # 1. Calculate pulse shape
            start_pulse = time.time()
            shape_params = self.get_current_shape_params()
            sequence = ShapedPulseSequence("Combined Calculation")
            sequence.add_shaped_pulse(
                np.pi / 2,
                self.params["pulse_duration"].get(),
                self.params["pulse_shape"].get(),
                shape_params,
                0.0,
                50,
                self.params["sx_amplitude"].get(),
                self.params["sy_amplitude"].get(),
            )
            pulse_shape = sequence.operations[0].get_pulse_shape()
            pulse_time = time.time() - start_pulse

            # 2. Calculate echo simulation
            start_echo = time.time()
            sequence.add_delay(self.params["tau"].get())
            sequence.add_shaped_pulse(
                np.pi,
                self.params["pulse_duration"].get(),
                self.params["pulse_shape"].get(),
                shape_params,
                0.0,
                50,
                self.params["sx_amplitude"].get(),
                self.params["sy_amplitude"].get(),
            )
            sequence.set_detection(
                self.params["dt"].get(),
                self.params["detection_points"].get(),
                ["sx", "sy"],
            )

            signals = self.simulator.simulate_sequence(
                sequence,
                detuning_range=(-8.0, 8.0),
                detuning_points=self.params["detuning_points"].get(),
                linewidth=self.params["linewidth"].get(),
                distribution_type="gaussian",
            )
            echo_time = time.time() - start_echo
            total_time = time.time() - start_total

            self.result_queue.put(
                (
                    "combined_success",
                    {
                        "pulse_shape": pulse_shape,
                        "signals": signals,
                        "times": {
                            "pulse": pulse_time,
                            "echo": echo_time,
                            "total": total_time,
                        },
                    },
                )
            )

        except Exception as e:
            self.result_queue.put(("error", str(e)))

    def _check_combined_results(self):
        """Check for combined calculation results."""
        try:
            result_type, data = self.result_queue.get_nowait()

            if result_type == "combined_success":
                # Update timing displays
                times = data["times"]
                self.calculation_times["pulse_shape"] = times["pulse"]
                self.calculation_times["echo"] = times["echo"]

                self.pulse_time_label.config(
                    text=f"Pulse shape: {times['pulse']:.2f} s"
                )
                self.echo_time_label.config(
                    text=f"Echo simulation: {times['echo']:.2f} s"
                )

                # Show combined results
                self.plot_combined_results(data["pulse_shape"], data["signals"])
                self.status_var.set(f"Calculation completed in {times['total']:.2f} s")
            else:
                messagebox.showerror("Calculation Error", f"Error: {data}")
                self.status_var.set("Calculation failed")

            self.simulation_running = False

        except queue.Empty:
            if self.simulation_running:
                self.root.after(100, self._check_combined_results)

    def plot_combined_results(self, pulse_shape, signals):
        """Plot combined results showing both pulse shape and echo signals."""
        self.fig.clear()

        # Create 3x2 subplot layout
        axes = self.fig.subplots(3, 2)

        # Get multiaxis parameters
        sx_amp = self.params["sx_amplitude"].get()
        sy_amp = self.params["sy_amplitude"].get()
        shape_name = self.params["pulse_shape"].get()

        # Calculate components
        if shape_name in ["wurst", "chirp"]:
            intrinsic_real = pulse_shape.amplitude * np.cos(pulse_shape.phase)
            intrinsic_imag = pulse_shape.amplitude * np.sin(pulse_shape.phase)
            applied_sx = intrinsic_real * sx_amp
            applied_sy = intrinsic_imag * sy_amp
        else:
            intrinsic_real = pulse_shape.amplitude * np.cos(pulse_shape.phase)
            intrinsic_imag = pulse_shape.amplitude * np.sin(pulse_shape.phase)
            applied_sx = intrinsic_real * sx_amp
            applied_sy = intrinsic_imag * sy_amp

        # Row 1: Pulse shape
        axes[0, 0].plot(
            pulse_shape.time_axis, pulse_shape.amplitude, "b-", linewidth=1.2
        )
        axes[0, 0].set_title("Pulse Amplitude", fontsize=9)
        axes[0, 0].set_ylabel("Amplitude", fontsize=8)
        axes[0, 0].grid(True, alpha=0.3)

        axes[0, 1].plot(pulse_shape.time_axis, pulse_shape.phase, "r-", linewidth=1.2)
        axes[0, 1].set_title("Pulse Phase", fontsize=9)
        axes[0, 1].set_ylabel("Phase (rad)", fontsize=8)
        axes[0, 1].grid(True, alpha=0.3)

        # Row 2: Real and imaginary components
        axes[1, 0].plot(
            pulse_shape.time_axis,
            intrinsic_real,
            "g-",
            linewidth=1.2,
            alpha=0.7,
            label="Intrinsic",
        )
        axes[1, 0].plot(
            pulse_shape.time_axis,
            applied_sx,
            "g-",
            linewidth=1.8,
            label=f"Applied (×{sx_amp})",
        )
        axes[1, 0].set_title("REAL Part (Sx)", fontsize=9)
        axes[1, 0].set_ylabel("Real Amplitude", fontsize=8)
        axes[1, 0].legend(fontsize=7)
        axes[1, 0].grid(True, alpha=0.3)

        axes[1, 1].plot(
            pulse_shape.time_axis,
            intrinsic_imag,
            "m-",
            linewidth=1.2,
            alpha=0.7,
            label="Intrinsic",
        )
        axes[1, 1].plot(
            pulse_shape.time_axis,
            applied_sy,
            "m-",
            linewidth=1.8,
            label=f"Applied (×{sy_amp})",
        )
        axes[1, 1].set_title("IMAGINARY Part (Sy)", fontsize=9)
        axes[1, 1].set_ylabel("Imaginary Amplitude", fontsize=8)
        axes[1, 1].legend(fontsize=7)
        axes[1, 1].grid(True, alpha=0.3)

        # Row 3: Echo signals - Sx and Sy separately
        time_axis = (
            np.arange(self.params["detection_points"].get()) * self.params["dt"].get()
        )
        sx_signal = np.real(signals["sx"])
        sy_signal = np.real(signals["sy"])

        axes[2, 0].plot(time_axis, sx_signal, "g-", linewidth=1.2)
        axes[2, 0].set_title("Sx Echo Signal (Real)", fontsize=9)
        axes[2, 0].set_xlabel("Time", fontsize=8)
        axes[2, 0].set_ylabel("Sx Amplitude", fontsize=8)
        axes[2, 0].axvline(
            self.params["tau"].get(),
            color="red",
            linestyle="--",
            alpha=0.7,
            label=f'Echo at τ={self.params["tau"].get():.1f}',
        )
        axes[2, 0].legend(fontsize=7)
        axes[2, 0].grid(True, alpha=0.3)

        axes[2, 1].plot(time_axis, sy_signal, "m-", linewidth=1.2)
        axes[2, 1].set_title("Sy Echo Signal (Imaginary)", fontsize=9)
        axes[2, 1].set_xlabel("Time", fontsize=8)
        axes[2, 1].set_ylabel("Sy Amplitude", fontsize=8)
        axes[2, 1].axvline(
            self.params["tau"].get(),
            color="red",
            linestyle="--",
            alpha=0.7,
            label=f'Echo at τ={self.params["tau"].get():.1f}',
        )
        axes[2, 1].legend(fontsize=7)
        axes[2, 1].grid(True, alpha=0.3)

        self.fig.suptitle(
            f"{shape_name.title()} Pulse & Echo Analysis\n"
            f"Applied: Sx={sx_amp:.1f}, Sy={sy_amp:.1f}",
            fontsize=10,
            fontweight="bold",
        )

        self.fig.tight_layout()
        self.canvas.draw()

    def show_pulse_shape(self):
        """Show just the pulse shape with timing."""
        try:
            start_time = time.time()
            self.status_var.set("Generating pulse shape...")
            self.root.update()

            # Create sequence
            shape_params = self.get_current_shape_params()
            sequence = ShapedPulseSequence("Test")
            sequence.add_shaped_pulse(
                np.pi / 2,
                self.params["pulse_duration"].get(),
                self.params["pulse_shape"].get(),
                shape_params,
                0.0,
                50,
                self.params["sx_amplitude"].get(),
                self.params["sy_amplitude"].get(),
            )

            # Get pulse shape
            pulse_shape = sequence.operations[0].get_pulse_shape()
            calc_time = time.time() - start_time

            # Update timing
            self.calculation_times["pulse_shape"] = calc_time
            self.pulse_time_label.config(text=f"Pulse shape: {calc_time:.3f} s")

            # Plot pulse shape components with CORRECTED calculation
            self.plot_pulse_shape_corrected(pulse_shape)
            self.status_var.set(f"Pulse shape displayed ({calc_time:.3f} s)")

        except Exception as e:
            messagebox.showerror("Error", f"Error showing pulse shape: {str(e)}")
            self.status_var.set("Error occurred")

    def plot_pulse_shape_corrected(self, pulse_shape):
        """Plot pulse shape with corrected real/imaginary components."""
        self.fig.clear()

        # Create subplots
        axes = self.fig.subplots(2, 3)

        # Get multiaxis parameters
        sx_amp = self.params["sx_amplitude"].get()
        sy_amp = self.params["sy_amplitude"].get()

        # CORRECTED: For frequency-swept pulses, show the intrinsic complex nature
        shape_name = self.params["pulse_shape"].get()

        if shape_name in ["wurst", "chirp"]:
            # For frequency-swept pulses, the complex field components are:
            # Real part: amplitude * cos(phase(t))  - intrinsic to the pulse
            # Imag part: amplitude * sin(phase(t))  - intrinsic to the pulse
            # Then scaled by sx_amp and sy_amp for the applied field
            intrinsic_real = pulse_shape.amplitude * np.cos(pulse_shape.phase)
            intrinsic_imag = pulse_shape.amplitude * np.sin(pulse_shape.phase)

            # Applied field components
            applied_sx = intrinsic_real * sx_amp
            applied_sy = intrinsic_imag * sy_amp
        else:
            # For non-frequency-swept pulses
            intrinsic_real = pulse_shape.amplitude * np.cos(pulse_shape.phase)
            intrinsic_imag = pulse_shape.amplitude * np.sin(pulse_shape.phase)

            # Applied field components
            applied_sx = intrinsic_real * sx_amp
            applied_sy = intrinsic_imag * sy_amp

        # Row 1: Pulse fundamentals
        axes[0, 0].plot(
            pulse_shape.time_axis, pulse_shape.amplitude, "b-", linewidth=1.2
        )
        axes[0, 0].set_title("Amplitude |Ω(t)|", fontsize=9)
        axes[0, 0].set_ylabel("Amplitude", fontsize=8)
        axes[0, 0].grid(True, alpha=0.3)

        axes[0, 1].plot(pulse_shape.time_axis, pulse_shape.phase, "r-", linewidth=1.2)
        axes[0, 1].set_title("Phase φ(t)", fontsize=9)
        axes[0, 1].set_ylabel("Phase (rad)", fontsize=8)
        axes[0, 1].grid(True, alpha=0.3)

        if np.any(pulse_shape.frequency != 0):
            axes[0, 2].plot(
                pulse_shape.time_axis, pulse_shape.frequency, "orange", linewidth=1.2
            )
            axes[0, 2].set_title("Frequency Sweep", fontsize=9)
            axes[0, 2].set_ylabel("Frequency", fontsize=8)
        else:
            axes[0, 2].text(
                0.5,
                0.5,
                "No Frequency\nModulation",
                transform=axes[0, 2].transAxes,
                ha="center",
                va="center",
                fontsize=8,
            )
            axes[0, 2].set_title("Frequency Modulation", fontsize=9)
        axes[0, 2].grid(True, alpha=0.3)

        # Row 2: Real and imaginary components
        axes[1, 0].plot(
            pulse_shape.time_axis,
            intrinsic_real,
            "g-",
            linewidth=1.2,
            label="Intrinsic",
        )
        axes[1, 0].plot(
            pulse_shape.time_axis,
            applied_sx,
            "g--",
            linewidth=1.2,
            label=f"Applied (×{sx_amp})",
        )
        axes[1, 0].set_title("REAL Part (Sx component)", fontsize=9)
        axes[1, 0].set_xlabel("Time", fontsize=8)
        axes[1, 0].set_ylabel("Real(Ω)", fontsize=8)
        axes[1, 0].legend(fontsize=7)
        axes[1, 0].grid(True, alpha=0.3)

        axes[1, 1].plot(
            pulse_shape.time_axis,
            intrinsic_imag,
            "m-",
            linewidth=1.2,
            label="Intrinsic",
        )
        axes[1, 1].plot(
            pulse_shape.time_axis,
            applied_sy,
            "m--",
            linewidth=1.2,
            label=f"Applied (×{sy_amp})",
        )
        axes[1, 1].set_title("IMAGINARY Part (Sy component)", fontsize=9)
        axes[1, 1].set_xlabel("Time", fontsize=8)
        axes[1, 1].set_ylabel("Imag(Ω)", fontsize=8)
        axes[1, 1].legend(fontsize=7)
        axes[1, 1].grid(True, alpha=0.3)

        # Combined plot
        axes[1, 2].plot(
            pulse_shape.time_axis, applied_sx, "g-", linewidth=1.2, label="Real Applied"
        )
        axes[1, 2].plot(
            pulse_shape.time_axis, applied_sy, "m-", linewidth=1.2, label="Imag Applied"
        )
        total_applied = np.sqrt(applied_sx**2 + applied_sy**2)
        axes[1, 2].plot(
            pulse_shape.time_axis, total_applied, "k--", linewidth=1.2, label="|Total|"
        )
        axes[1, 2].set_title("Applied Field Components", fontsize=9)
        axes[1, 2].set_xlabel("Time", fontsize=8)
        axes[1, 2].set_ylabel("Amplitude", fontsize=8)
        axes[1, 2].legend(fontsize=7)
        axes[1, 2].grid(True, alpha=0.3)

        self.fig.suptitle(
            f"{shape_name.title()} Pulse Shape\n"
            f"Applied: Sx={sx_amp:.1f}, Sy={sy_amp:.1f}",
            fontsize=10,
            fontweight="bold",
        )

        self.fig.tight_layout()
        self.canvas.draw()

    def run_simulation(self):
        """Run the full simulation with timing."""
        if self.simulation_running:
            messagebox.showwarning("Warning", "Simulation already running!")
            return

        self.simulation_running = True

        # Update n_jobs in simulator
        self.simulator.n_jobs = self.params["n_jobs"].get()
        self.jobs_var.set(f"Jobs: {self.params['n_jobs'].get()}")

        self.status_var.set("Running echo simulation...")

        # Run simulation in separate thread
        threading.Thread(target=self._simulation_thread, daemon=True).start()

        # Check for results
        self.root.after(100, self._check_simulation_results)

    def _simulation_thread(self):
        """Run simulation in separate thread with timing."""
        try:
            start_time = time.time()

            # Create sequence
            shape_params = self.get_current_shape_params()
            sequence = (
                ShapedPulseSequence("GUI Simulation")
                .add_shaped_pulse(
                    np.pi / 2,
                    self.params["pulse_duration"].get(),
                    self.params["pulse_shape"].get(),
                    shape_params,
                    0.0,
                    50,
                    self.params["sx_amplitude"].get(),
                    self.params["sy_amplitude"].get(),
                )
                .add_delay(self.params["tau"].get())
                .add_shaped_pulse(
                    np.pi,
                    self.params["pulse_duration"].get(),
                    self.params["pulse_shape"].get(),
                    shape_params,
                    0.0,
                    50,
                    self.params["sx_amplitude"].get(),
                    self.params["sy_amplitude"].get(),
                )
                .set_detection(
                    self.params["dt"].get(),
                    self.params["detection_points"].get(),
                    ["sx", "sy"],
                )
            )

            # Run simulation
            signals = self.simulator.simulate_sequence(
                sequence,
                detuning_range=(-8.0, 8.0),
                detuning_points=self.params["detuning_points"].get(),
                linewidth=self.params["linewidth"].get(),
                distribution_type="gaussian",
            )

            # Get pulse shape for plotting
            pulse_shape = sequence.operations[0].get_pulse_shape()

            calc_time = time.time() - start_time

            self.result_queue.put(("success", signals, pulse_shape, calc_time))

        except Exception as e:
            self.result_queue.put(("error", str(e), None, 0))

    def _check_simulation_results(self):
        """Check for simulation results."""
        try:
            result_type, data, pulse_shape, calc_time = self.result_queue.get_nowait()

            if result_type == "success":
                # Update timing
                self.calculation_times["echo"] = calc_time
                self.echo_time_label.config(text=f"Echo simulation: {calc_time:.2f} s")

                self.plot_simulation_results(data, pulse_shape)
                self.status_var.set(f"Echo simulation completed in {calc_time:.2f} s")
            else:
                messagebox.showerror("Simulation Error", f"Error: {data}")
                self.status_var.set("Simulation failed")

            self.simulation_running = False

        except queue.Empty:
            if self.simulation_running:
                self.root.after(100, self._check_simulation_results)

    def plot_simulation_results(self, signals, pulse_shape):
        """Plot the simulation results."""
        self.fig.clear()

        # Create subplots
        axes = self.fig.subplots(2, 2)

        # Create time axis
        time_axis = (
            np.arange(self.params["detection_points"].get()) * self.params["dt"].get()
        )

        # Extract signals
        sx_signal = np.real(signals["sx"])
        sy_signal = np.real(signals["sy"])
        magnitude = np.sqrt(sx_signal**2 + sy_signal**2)

        # Plot signals
        axes[0, 0].plot(time_axis, sx_signal, "g-", linewidth=1.2)
        axes[0, 0].set_title("Sx Signal (Real)", fontsize=9)
        axes[0, 0].set_ylabel("Sx", fontsize=8)
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].axvline(
            self.params["tau"].get(), color="red", linestyle="--", alpha=0.7
        )

        axes[0, 1].plot(time_axis, sy_signal, "m-", linewidth=1.2)
        axes[0, 1].set_title("Sy Signal (Imaginary)", fontsize=9)
        axes[0, 1].set_ylabel("Sy", fontsize=8)
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].axvline(
            self.params["tau"].get(), color="red", linestyle="--", alpha=0.7
        )

        axes[1, 0].plot(time_axis, magnitude, "b-", linewidth=1.2)
        axes[1, 0].set_title("Total Magnetization |Sxy|", fontsize=9)
        axes[1, 0].set_xlabel("Time", fontsize=8)
        axes[1, 0].set_ylabel("|Sxy|", fontsize=8)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].axvline(
            self.params["tau"].get(), color="red", linestyle="--", alpha=0.7
        )

        # Echo detail
        echo_time = self.params["tau"].get()
        echo_start = max(0, int((echo_time - 1.0) / self.params["dt"].get()))
        echo_end = min(len(magnitude), int((echo_time + 1.0) / self.params["dt"].get()))

        axes[1, 1].plot(
            time_axis[echo_start:echo_end],
            magnitude[echo_start:echo_end],
            "b-",
            linewidth=1.8,
        )
        axes[1, 1].set_title(f"Echo Detail (t ≈ {echo_time:.1f})", fontsize=9)
        axes[1, 1].set_xlabel("Time", fontsize=8)
        axes[1, 1].set_ylabel("|Sxy|", fontsize=8)
        axes[1, 1].grid(True, alpha=0.3)

        # Calculate and display results
        max_signal = np.max(magnitude)
        echo_amplitude = (
            np.max(magnitude[echo_start:echo_end]) if echo_start < echo_end else 0
        )
        efficiency = (echo_amplitude / max_signal * 100) if max_signal > 0 else 0

        self.fig.suptitle(
            f'{self.params["pulse_shape"].get().title()} Echo Results\n'
            f"Max: {max_signal:.3f}, Echo: {echo_amplitude:.3f}, "
            f"Efficiency: {efficiency:.1f}% (Echo at τ={echo_time:.1f})",
            fontsize=10,
            fontweight="bold",
        )

        self.fig.tight_layout()
        self.canvas.draw()


def main():
    """Main function to run the GUI."""
    root = tk.Tk()
    app = PulseExplorerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
