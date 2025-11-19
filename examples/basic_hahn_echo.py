#!/usr/bin/env python3
"""
Basic Hahn Echo Simulation Example

This script demonstrates a simple 2-pulse Hahn echo sequence:
    π/2 - τ - π - τ - echo

The echo forms at time t = 2τ, refocusing the dephasing that occurs
during the free evolution periods.

Author: Sylvain Bertaina
"""

import matplotlib.pyplot as plt
import numpy as np

from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator

# ============================================================================
# PARAMETERS
# ============================================================================

# Echo delay (time units)
tau = 5.0

# Pulse parameters
pulse_duration = 1.0
pulse_shape = "gaussian"
sigma_factor = 3.0

# Simulation parameters
linewidth = 2.0
detuning_points = 51
n_jobs = 4  # Number of parallel jobs

# Detection parameters
dt = 0.01
detection_points = 1000

# ============================================================================
# CREATE SEQUENCE
# ============================================================================

print("Creating Hahn Echo sequence...")
print(f"  Echo delay (τ): {tau}")
print(f"  Pulse shape: {pulse_shape}")
print(f"  Pulse duration: {pulse_duration}")

sequence = (
    ShapedPulseSequence("Hahn Echo")
    # First pulse: π/2 (90°)
    .add_shaped_pulse(
        flip_angle=np.pi / 2,
        duration=pulse_duration,
        shape_type=pulse_shape,
        shape_params={"sigma_factor": sigma_factor},
    )
    # Free evolution delay τ
    .add_delay(tau)
    # Second pulse: π (180°) for refocusing
    .add_shaped_pulse(
        flip_angle=np.pi,
        duration=pulse_duration,
        shape_type=pulse_shape,
        shape_params={"sigma_factor": sigma_factor},
    )
    # Free evolution delay τ
    .add_delay(tau)
    # Set up detection (detect all three components)
    .set_detection(dt=dt, points=detection_points, detect_axes=["sx", "sy", "sz"])
)

print(f"✓ Sequence created with {len(sequence.operations)} operations")

# ============================================================================
# RUN SIMULATION
# ============================================================================

print("\nRunning simulation...")
print(f"  Linewidth: {linewidth}")
print(f"  Detuning points: {detuning_points}")
print(f"  Parallel jobs: {n_jobs}")

simulator = ShapedSpinEchoSimulator(n_jobs=n_jobs)

result = simulator.simulate_sequence(
    sequence,
    linewidth=linewidth,
    distribution_type="gaussian",
    detuning_points=detuning_points,
)

print("✓ Simulation complete!")

# ============================================================================
# ANALYZE RESULTS
# ============================================================================

# Generate time axis from detection parameters
time = np.arange(detection_points) * dt

# Find echo peak
echo_time_expected = 2 * tau
echo_index = np.argmin(np.abs(time - echo_time_expected))
echo_amplitude = result["sy"][echo_index]

print("\nResults:")
print(f"  Expected echo time: {echo_time_expected:.2f}")
print(f"  Echo amplitude: {echo_amplitude:.4f}")
print(f"  Echo efficiency: {abs(echo_amplitude)*100:.1f}%")

# ============================================================================
# PLOT RESULTS
# ============================================================================

print("\nGenerating plots...")

fig, axes = plt.subplots(2, 2, figsize=(12, 8))

# Plot Sx component
axes[0, 0].plot(time, result["sx"], "b-", linewidth=2)
axes[0, 0].axvline(
    echo_time_expected, color="r", linestyle="--", alpha=0.5, label="Expected echo"
)
axes[0, 0].set_xlabel("Time")
axes[0, 0].set_ylabel("Sx")
axes[0, 0].set_title("Transverse Magnetization (Sx)")
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].legend()

# Plot Sy component
axes[0, 1].plot(time, result["sy"], "g-", linewidth=2)
axes[0, 1].axvline(
    echo_time_expected, color="r", linestyle="--", alpha=0.5, label="Expected echo"
)
axes[0, 1].set_xlabel("Time")
axes[0, 1].set_ylabel("Sy")
axes[0, 1].set_title("Transverse Magnetization (Sy)")
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].legend()

# Plot Sz component
axes[1, 0].plot(time, result["sz"], "r-", linewidth=2)
axes[1, 0].set_xlabel("Time")
axes[1, 0].set_ylabel("Sz")
axes[1, 0].set_title("Longitudinal Magnetization (Sz)")
axes[1, 0].grid(True, alpha=0.3)

# Plot total magnetization
total_mag = np.sqrt(result["sx"] ** 2 + result["sy"] ** 2 + result["sz"] ** 2)
axes[1, 1].plot(time, total_mag, "k-", linewidth=2)
axes[1, 1].set_xlabel("Time")
axes[1, 1].set_ylabel("|M|")
axes[1, 1].set_title("Total Magnetization")
axes[1, 1].grid(True, alpha=0.3)

plt.suptitle(
    f"Hahn Echo Simulation (τ = {tau}, linewidth = {linewidth})",
    fontsize=14,
    fontweight="bold",
)
plt.tight_layout()

# Save figure
output_file = "hahn_echo_result.png"
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"✓ Plot saved to: {output_file}")

plt.show()

print("\n" + "=" * 70)
print("SIMULATION COMPLETE!")
print("=" * 70)
