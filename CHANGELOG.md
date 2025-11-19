# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- English translations for all GUI strings and docstrings
- Multilingual documentation structure (English and French)
- README badges for Python version, license, code style, and platform
- Table of contents in README
- Documentation index with language navigation
- This CHANGELOG file

### Changed
- GUI plot labels translated from French to English ("Temps" → "Time", "Amplitude du Signal" → "Signal Amplitude")
- Module docstrings translated to English in GUI files
- Improved README structure with documentation links

### Documentation
- Created `docs/` directory with language-specific subdirectories
- Added comprehensive English documentation:
  - QUICKSTART_EN.md
  - INSTALLATION.md
  - PROJECT_INFO_EN.md
- Maintained French documentation:
  - QUICKSTART.md (fr)
  - INSTALLATION_FR.md (fr)
  - PROJECT_INFO.md (fr)
- Added docs/README.md as multilingual documentation index

## [1.0.0] - 2024-11-02

### Added
- Initial standalone package extraction from parent PulseSeq project
- Three GUI applications:
  - Basic Spin Echo GUI (parallel version)
  - Basic Spin Echo GUI (single-core version)
  - Shaped Pulse Explorer GUI
- Core simulation frameworks:
  - `spinecho.py` - Flexible sequence framework
  - `spinechoshaped.py` - Advanced shaped pulse framework
- CLI commands:
  - `pulseechogui-basic` - Launch parallel GUI
  - `pulseechogui-basic-single` - Launch single-core GUI
  - `pulseechogui-shaped` - Launch shaped pulse GUI
  - `pulseechogui-validate` - Validate installation
- Quick launcher script (`run_gui.py`)
- Modern Python packaging with `pyproject.toml`
- Legacy setup.py for backward compatibility
- Complete README documentation
- MIT License

### Features
- Quantum mechanical simulation using density matrix formalism
- Support for multiple pulse shapes:
  - Gaussian
  - Square
  - SECH (hyperbolic secant adiabatic)
  - WURST (wideband uniform rate smooth truncation)
  - Chirped (linear frequency sweep)
  - Noisy (realistic experimental pulses)
- Multi-axis control (independent Sx/Sy amplitudes)
- Distribution averaging (Gaussian, Lorentzian, exponential, uniform)
- Parallel processing with joblib
- Real-time parameter modification in GUIs
- Phase cycling support
- Time-sliced evolution for shaped pulses
- Physics validation (unitarity, conservation laws)

### Dependencies
- Python >= 3.8
- numpy >= 1.20.0
- scipy >= 1.7.0
- matplotlib >= 3.5.0
- joblib >= 1.1.0
- tkinter (bundled with Python)

### Development Tools
- Black for code formatting
- isort for import sorting
- flake8 for linting
- Type hints (Python 3.8+ compatible)

---

## Version History Summary

- **1.0.0** (2024-11-02): Initial standalone package release
- **Unreleased**: Internationalization improvements

---

## Links

- [Repository](https://github.com/sylvainbertaina/PulseSeq)
- [Issues](https://github.com/sylvainbertaina/PulseSeq/issues)
- [Parent Project - PulseSeq](https://github.com/sylvainbertaina/PulseSeq)

---

## Contribution Guidelines

When adding entries to this changelog:

1. **Version sections** should follow semantic versioning (MAJOR.MINOR.PATCH)
2. **Unreleased** section at top for upcoming changes
3. **Categories** for changes:
   - `Added` - New features
   - `Changed` - Changes in existing functionality
   - `Deprecated` - Soon-to-be removed features
   - `Removed` - Removed features
   - `Fixed` - Bug fixes
   - `Security` - Security fixes
   - `Documentation` - Documentation-only changes
   - `Performance` - Performance improvements

4. **Date format**: YYYY-MM-DD (ISO 8601)
5. **Keep entries concise** but descriptive
6. **Link to issues/PRs** when applicable: `(#123)` or `[#123](url)`

---

**Contact**: Sylvain Bertaina (sylvain.bertaina@cnrs.fr)
