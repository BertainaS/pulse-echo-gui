# Screenshots and Images

This directory contains screenshots and images for documentation.

## Required Screenshots

To complete the documentation, please add the following screenshots:

### 1. Basic Spin Echo GUI (Parallel)
**File name:** `basic_gui_parallel.png`
**Command to launch:** `pulseechogui-basic`

**What to capture:**
- Main window with all parameter controls
- Plot showing a typical Hahn echo simulation
- Should show 2-pulse echo formation at t ≈ 2τ

**Recommended settings for screenshot:**
- Echo delay (τ): 5.0
- Detuning: 2.0
- Linewidth: 2.0
- Pulse type: Hard
- Number of detuning points: 51

### 2. Basic Spin Echo GUI (Single-Core)
**File name:** `basic_gui_single.png`
**Command to launch:** `pulseechogui-basic-single`

**What to capture:**
- Similar to parallel version
- 3-pulse stimulated echo sequence if possible
- Show parameter panel clearly

### 3. Shaped Pulse Explorer GUI
**File name:** `shaped_pulse_gui.png`
**Command to launch:** `pulseechogui-shaped`

**What to capture:**
- Main window with pulse shape selector
- Pulse shape visualization panel
- Echo simulation result
- Multi-axis controls visible

**Recommended settings:**
- Pulse shape: Gaussian
- Flip angle: π/2
- Pulse duration: 1.0
- Sigma factor: 3.0

### 4. WURST Pulse Example
**File name:** `wurst_pulse_example.png`
**Command:** `pulseechogui-shaped`

**What to capture:**
- WURST pulse shape visualization
- Frequency sweep parameters visible
- Simulation result showing broadband excitation

**Recommended settings:**
- Pulse shape: WURST
- Pulse duration: 2.0
- Frequency start: -10
- Frequency end: 10
- WURST n: 2

### 5. Comparison of Pulse Shapes
**File name:** `pulse_shapes_comparison.png`

**What to capture:**
- Multiple pulse shapes side by side
- Show Gaussian, SECH, WURST, and Chirped
- Can be created using programmatic approach

### 6. Echo Formation Animation (Optional)
**File name:** `echo_formation.gif`

**What to create:**
- Animation showing magnetization evolution
- Dephasing during first delay
- Refocusing after π pulse
- Echo formation at t = 2τ

## Screenshot Guidelines

### Technical Requirements

- **Resolution:** Minimum 1920x1080 (high DPI recommended)
- **Format:** PNG for static images, GIF for animations
- **Color depth:** 24-bit RGB minimum
- **Compression:** Use lossless compression
- **File size:** Keep under 2 MB per image (optimize if needed)

### Capture Instructions

#### On macOS:
```bash
# Full window capture (Cmd+Shift+4, then Space, then click window)
# Or use screencapture command
screencapture -w -o gui_screenshot.png
```

#### On Linux:
```bash
# Using gnome-screenshot
gnome-screenshot -w -f gui_screenshot.png

# Or using scrot
scrot -u gui_screenshot.png
```

#### On Windows:
```bash
# Use Windows+Shift+S for Snipping Tool
# Or use PowerShell
Add-Type -AssemblyName System.Windows.Forms
[System.Windows.Forms.SendKeys]::SendWait("%{PRTSC}")
```

### Image Optimization

After capturing screenshots:

```bash
# Install optipng for optimization
# Ubuntu/Debian
sudo apt-get install optipng

# macOS
brew install optipng

# Optimize PNG files
optipng -o7 *.png
```

### Adding Screenshots to Documentation

Once screenshots are added, update the following files:

1. **README.md** - Add image at the top:
   ```markdown
   ![PulseEchoGui GUI](docs/images/basic_gui_parallel.png)
   ```

2. **docs/en/QUICKSTART.md** - Add GUI screenshots:
   ```markdown
   ## GUI Applications

   ### Basic Spin Echo GUI
   ![Basic GUI](../images/basic_gui_parallel.png)
   ```

3. **docs/en/INSTALLATION.md** - Add visual guides

## Creating Programmatic Screenshots

For pulse shape comparisons, use this Python script:

```python
import numpy as np
import matplotlib.pyplot as plt
from pulseechogui import ShapedPulseSequence

# Create figure
fig, axes = plt.subplots(2, 2, figsize=(12, 8))

shapes = ['gaussian', 'sech', 'wurst', 'chirped']
titles = ['Gaussian', 'SECH', 'WURST', 'Chirped']

for ax, shape, title in zip(axes.flat, shapes, titles):
    # Create sequence with specific shape
    seq = ShapedPulseSequence(f"{title} Pulse")
    seq.add_shaped_pulse(np.pi/2, 2.0, shape)

    # Plot pulse shape
    # (implementation depends on your API)
    ax.set_title(f'{title} Pulse Shape')
    ax.set_xlabel('Time')
    ax.set_ylabel('Amplitude')
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('docs/images/pulse_shapes_comparison.png', dpi=300)
```

## Animation Creation

For creating GIF animations:

```bash
# Install ImageMagick
# Ubuntu/Debian
sudo apt-get install imagemagick

# macOS
brew install imagemagick

# Create GIF from PNG sequence
convert -delay 10 -loop 0 frame*.png echo_formation.gif

# Optimize GIF
gifsicle -O3 --colors 256 echo_formation.gif -o echo_formation_opt.gif
```

## Checklist

Once screenshots are added:

- [ ] All required screenshots captured
- [ ] Images optimized for size
- [ ] Images added to this directory
- [ ] README.md updated with main GUI screenshot
- [ ] Documentation files updated with relevant images
- [ ] Image references working in rendered Markdown
- [ ] Screenshots show representative parameter values
- [ ] GUI elements clearly visible and readable
- [ ] Professional appearance (clean desktop, proper window sizing)

## Notes

- Screenshots should represent typical usage scenarios
- Avoid showing personal information or file paths
- Use standard theme/appearance when possible
- Ensure text is readable at documentation rendering size
- Consider adding annotations (arrows, labels) for clarity
- Keep screenshots up-to-date when GUI changes

## Contact

For questions about screenshots or image guidelines:
- Email: sylvain.bertaina@cnrs.fr
- See: [CONTRIBUTING.md](../../CONTRIBUTING.md)

---

**Last updated:** November 2, 2024
