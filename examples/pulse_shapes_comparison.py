#!/usr/bin/env python3
"""
Pulse Shapes Comparison

This script compares different pulse shapes:
- Gaussian: Smooth envelope, frequency selective
- Square: Step function, broadband
- SECH: Adiabatic hyperbolic secant
- WURST: Frequency-swept adiabatic pulse

Each pulse shape has different characteristics and applications.

Author: Sylvain Bertaina
"""

import matplotlib.pyplot as plt
import numpy as np

from pulseechogui import ShapedPulseSequence, ShapedSpinEchoSimulator

# ============================================================================
# PARAMETERS
# ============================================================================

# Common parameters
tau = 5.0
pulse_duration = 2.0
linewidth = 2.0
detuning_points = 31  # Reduced for faster comparison
n_jobs = 4

# Detection
dt = 0.01
detection_points = 800

# Pulse shapes to compare
pulse_shapes = {
    "gaussian": {"name": "Gaussian", "color": "blue", "params": {"sigma_factor": 3.0}},
    "square": {"name": "Square", "color": "green", "params": {}},
    "sech": {"name": "SECH (Adiabatic)", "color": "red", "params": {"beta": 5.0}},
    "wurst": {
        "name": "WURST (Frequency Sweep)",
        "color": "purple",
        "params": {"freq_start": -10, "freq_end": 10, "wurst_n": 2},
    },
}

# ============================================================================
# RUN SIMULATIONS
# ============================================================================

print("=" * 70)
print("PULSE SHAPES COMPARISON")
print("=" * 70)

results = {}
simulator = ShapedSpinEchoSimulator(n_jobs=n_jobs)

for shape_key, shape_info in pulse_shapes.items():
    print(f"\nSimulating {shape_info['name']} pulse...")

    # Create sequence
    sequence = (
        ShapedPulseSequence(f"{shape_info['name']} Echo")
        .add_shaped_pulse(
            flip_angle=np.pi / 2,
            duration=pulse_duration,
            shape_type=shape_key,
            shape_params=shape_info["params"] if shape_info["params"] else None,
        )
        .add_delay(tau)
        .set_detection(dt=dt, points=detection_points)
    )

    # Simulate
    result = simulator.simulate_sequence(
        sequence, linewidth=linewidth, detuning_points=detuning_points
    )

    results[shape_key] = result
    print(f"  ✓ Complete")

print("\n" + "=" * 70)

# ============================================================================
# ANALYZE RESULTS
# ============================================================================

# Generate time axis from detection parameters
time = np.arange(detection_points) * dt

print("\nRESULTS ANALYSIS")
print("=" * 70)

for shape_key, shape_info in pulse_shapes.items():
    result = results[shape_key]

    # Find maximum signal
    max_sy = np.max(np.abs(result["sy"]))
    max_idx = np.argmax(np.abs(result["sy"]))
    time_at_max = time[max_idx]

    print(f"\n{shape_info['name']}:")
    print(f"  Max signal amplitude: {max_sy:.4f}")
    print(f"  Time of max signal: {time_at_max:.2f}")
    print(f"  Relative efficiency: {max_sy*100:.1f}%")

# ============================================================================
# PLOT COMPARISONS
# ============================================================================

print("\nGenerating comparison plots...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Sy comparison
ax = axes[0, 0]
for shape_key, shape_info in pulse_shapes.items():
    result = results[shape_key]
    ax.plot(
        time,
        result["sy"],
        label=shape_info["name"],
        color=shape_info["color"],
        linewidth=2,
        alpha=0.7,
    )

ax.set_xlabel("Time", fontsize=12)
ax.set_ylabel("Sy (Transverse Magnetization)", fontsize=12)
ax.set_title(
    "Comparison of Pulse Shapes - Sy Component", fontsize=13, fontweight="bold"
)
ax.legend(fontsize=10, loc="best")
ax.grid(True, alpha=0.3)

# Plot 2: Sx comparison
ax = axes[0, 1]
for shape_key, shape_info in pulse_shapes.items():
    result = results[shape_key]
    ax.plot(
        time,
        result["sx"],
        label=shape_info["name"],
        color=shape_info["color"],
        linewidth=2,
        alpha=0.7,
    )

ax.set_xlabel("Time", fontsize=12)
ax.set_ylabel("Sx (Transverse Magnetization)", fontsize=12)
ax.set_title(
    "Comparison of Pulse Shapes - Sx Component", fontsize=13, fontweight="bold"
)
ax.legend(fontsize=10, loc="best")
ax.grid(True, alpha=0.3)

# Plot 3: Total transverse magnetization
ax = axes[1, 0]
for shape_key, shape_info in pulse_shapes.items():
    result = results[shape_key]
    transverse = np.sqrt(result["sx"] ** 2 + result["sy"] ** 2)
    ax.plot(
        time,
        transverse,
        label=shape_info["name"],
        color=shape_info["color"],
        linewidth=2,
        alpha=0.7,
    )

ax.set_xlabel("Time", fontsize=12)
ax.set_ylabel("|Mxy| (Total Transverse)", fontsize=12)
ax.set_title("Total Transverse Magnetization", fontsize=13, fontweight="bold")
ax.legend(fontsize=10, loc="best")
ax.grid(True, alpha=0.3)

# Plot 4: Efficiency comparison (bar chart)
ax = axes[1, 1]
shape_names = [info["name"] for info in pulse_shapes.values()]
efficiencies = [np.max(np.abs(results[key]["sy"])) * 100 for key in pulse_shapes.keys()]
colors = [info["color"] for info in pulse_shapes.values()]

bars = ax.bar(
    range(len(shape_names)), efficiencies, color=colors, alpha=0.7, edgecolor="black"
)
ax.set_xticks(range(len(shape_names)))
ax.set_xticklabels(shape_names, rotation=15, ha="right")
ax.set_ylabel("Signal Efficiency (%)", fontsize=12)
ax.set_title("Pulse Shape Efficiency Comparison", fontsize=13, fontweight="bold")
ax.grid(True, axis="y", alpha=0.3)

# Add value labels on bars
for bar, eff in zip(bars, efficiencies):
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2.0,
        height,
        f"{eff:.1f}%",
        ha="center",
        va="bottom",
        fontsize=10,
    )

plt.suptitle(
    "Pulse Shapes Comparison - NMR/ESR Simulations",
    fontsize=16,
    fontweight="bold",
    y=0.995,
)
plt.tight_layout()

# Save
output_file = "pulse_shapes_comparison.png"
plt.savefig(output_file, dpi=300, bbox_inches="tight")
print(f"✓ Plot saved to: {output_file}")

plt.show()

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "=" * 70)
print("COMPARISON SUMMARY")
print("=" * 70)
print("\nKey Observations:")
print("  • Gaussian: Good general-purpose pulse, frequency selective")
print("  • Square: Broadband excitation, less selective")
print("  • SECH: Adiabatic passage, robust to amplitude errors")
print("  • WURST: Frequency-swept, excellent for broad excitation")
print("\nUse Case Recommendations:")
print("  • Narrow resonances → Gaussian")
print("  • Broad distributions → WURST")
print("  • Amplitude robustness → SECH")
print("  • Fast excitation → Square")
print("=" * 70)
