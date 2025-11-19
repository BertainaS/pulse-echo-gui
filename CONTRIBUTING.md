# Contributing to PulseEchoGui

Thank you for your interest in contributing to PulseEchoGui! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Questions](#questions)

## Code of Conduct

This project adheres to a code of professional and respectful conduct. By participating, you are expected to:

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/PulseEchoGui.git
   cd PulseEchoGui
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/sylvainbertaina/PulseSeq.git
   ```
4. **Create a branch** for your changes:
   ```bash
   git checkout -b feature/my-new-feature
   ```

## Development Setup

### Prerequisites

- Python >= 3.8
- pip
- git

### Install in Development Mode

```bash
# Install package with development dependencies
pip install -e ".[dev]"

# Or install all optional dependencies
pip install -e ".[all]"
```

### Verify Installation

```bash
# Run validation
pulseechogui-validate

# Test imports
python -c "import pulseechogui; print(pulseechogui.__version__)"
```

## How to Contribute

### Types of Contributions

We welcome several types of contributions:

1. **Bug fixes** - Fix issues in existing code
2. **New features** - Add new pulse shapes, GUI improvements, etc.
3. **Documentation** - Improve docs, add examples, fix typos
4. **Tests** - Add unit tests, integration tests
5. **Performance** - Optimization and profiling improvements
6. **Translations** - Add or improve translations (currently English/French)

### Contribution Workflow

1. **Check existing issues** to avoid duplicate work
2. **Open an issue** to discuss major changes before starting
3. **Make your changes** following coding standards
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Update CHANGELOG.md** with your changes
7. **Submit a pull request**

## Coding Standards

### Python Style

This project follows strict Python best practices:

- **PEP 8** compliance
- **Black** for code formatting (line length: 88)
- **isort** for import sorting
- **flake8** for linting
- **Type hints** for all public API functions (Python 3.8+)

### Running Code Quality Tools

```bash
# Format code
black pulseechogui/
isort pulseechogui/

# Check linting
flake8 pulseechogui/

# Type checking (if using mypy)
mypy pulseechogui/
```

### Pre-commit Hooks

We recommend using pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Code Structure Guidelines

1. **Modules**: One framework per file, clear responsibilities
2. **Classes**: Follow builder pattern for sequence construction
3. **Functions**: Pure functions when possible, clear inputs/outputs
4. **Docstrings**: NumPy format with mathematical notation
5. **Comments**: Explain "why", not "what"

### Example Function Template

```python
def my_function(param1: float, param2: str = "default") -> np.ndarray:
    """
    Brief description of function.

    Detailed explanation with physics background if relevant.

    Parameters
    ----------
    param1 : float
        Description with typical values and units
    param2 : str, optional
        Description (default: "default")

    Returns
    -------
    result : np.ndarray, shape (N,)
        Description of return value

    Raises
    ------
    ValueError
        If parameter validation fails

    Examples
    --------
    >>> my_function(1.0, "test")
    array([...])

    Notes
    -----
    Additional implementation details or references.
    """
    # Implementation
    pass
```

## Testing Guidelines

### Writing Tests

- Use **pytest** framework
- Test both success and failure cases
- Validate physics (unitarity, conservation laws)
- Include edge cases

### Test Structure

```python
def test_feature_name():
    """Test description."""
    # Arrange
    input_data = create_test_data()

    # Act
    result = function_under_test(input_data)

    # Assert
    assert result.property == expected_value
    np.testing.assert_allclose(result.array, expected_array)
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pulseechogui

# Run specific test file
pytest tests/test_spinecho.py
```

## Documentation

### Docstring Format

Use **NumPy docstring format**:

- Brief description (one line)
- Extended summary (optional)
- Parameters section
- Returns section
- Raises section (if applicable)
- Examples section (encouraged)
- Notes section (for physics/math details)

### Mathematical Notation

Use LaTeX in docstrings for equations:

```python
"""
Calculate rotation operator.

The evolution operator is:
    U = exp(-i·θ·Sφ)
where Sφ = cos(φ)·Sx + sin(φ)·Sy
"""
```

### Updating Documentation

When making changes:

1. **Update docstrings** in code
2. **Update relevant .md files** in docs/
3. **Update both English and French** versions
4. **Add examples** if introducing new features
5. **Update CHANGELOG.md**

## Commit Messages

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style (formatting, no code change)
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `test`: Adding tests
- `chore`: Maintenance (dependencies, build, etc.)

### Examples

```bash
# Good commit messages
git commit -m "feat(gui): add export to CSV functionality"
git commit -m "fix(spinecho): correct phase convention in evolution operator"
git commit -m "docs: add WURST pulse tutorial"

# Bad commit messages (avoid these)
git commit -m "fixed bug"
git commit -m "updates"
git commit -m "work in progress"
```

## Pull Request Process

### Before Submitting

1. ✅ Code follows style guidelines (black, isort, flake8)
2. ✅ All tests pass
3. ✅ New features have tests
4. ✅ Documentation is updated
5. ✅ CHANGELOG.md is updated
6. ✅ Commits are clean and descriptive

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation
- [ ] Performance improvement
- [ ] Refactoring

## Testing
Describe testing performed

## Checklist
- [ ] Code follows style guidelines
- [ ] Tests pass
- [ ] Documentation updated
- [ ] CHANGELOG updated
```

### Review Process

1. Maintainer reviews code
2. Automated checks run (if CI/CD is set up)
3. Feedback addressed
4. PR approved and merged

## Reporting Bugs

### Before Reporting

- Check existing issues
- Verify it's actually a bug (not expected behavior)
- Test with latest version

### Bug Report Template

When reporting bugs, include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Minimal example
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**:
   - OS (macOS, Linux, Windows)
   - Python version
   - PulseEchoGui version
   - Dependencies versions
6. **Code example**: Minimal reproducible example
7. **Error messages**: Full traceback if applicable

## Suggesting Enhancements

### Feature Request Template

1. **Summary**: Brief description
2. **Motivation**: Why is this needed?
3. **Proposed solution**: How should it work?
4. **Alternatives considered**: Other approaches
5. **Additional context**: Screenshots, references

### Examples of Good Enhancement Requests

- New pulse shapes (with physics references)
- GUI improvements (with mockups)
- Performance optimizations (with benchmarks)
- Additional export formats

## Questions

### Where to Ask

- **GitHub Issues**: For bugs and feature requests
- **Email**: sylvain.bertaina@cnrs.fr for general questions
- **Documentation**: Check docs/ first

### Getting Help

If you're stuck:

1. Check existing documentation
2. Search closed issues
3. Ask in a new issue with "question" label
4. Provide context and what you've tried

## Scientific Contributions

### Physics Accuracy

When contributing physics-related code:

- **Cite references** for new methods
- **Validate results** against known analytical solutions
- **Document conventions** (phase, units, etc.)
- **Test conservation laws**

### Example Scientific Contribution

```python
def adiabatic_evolution(beta: float) -> np.ndarray:
    """
    Calculate adiabatic evolution operator.

    Implements the adiabatic passage technique described in:
    Baum et al., J. Chem. Phys. 79, 4643 (1983).

    Parameters
    ----------
    beta : float
        Adiabaticity parameter (β > 5 recommended)

    Notes
    -----
    The adiabatic condition requires:
        |dθ/dt| << ω₁²/|dω₁/dt|
    where θ is the effective field angle.
    """
    # Implementation with validation
    pass
```

## Recognition

Contributors will be:

- Listed in CHANGELOG.md
- Acknowledged in releases
- Credited in citations (for significant contributions)

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

## Contact

**Maintainer**: Sylvain Bertaina
**Email**: sylvain.bertaina@cnrs.fr
**Institution**: CNRS (Centre National de la Recherche Scientifique)

---

Thank you for contributing to PulseEchoGui! 🎉
