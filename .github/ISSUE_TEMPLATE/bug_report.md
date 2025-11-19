---
name: Bug Report
about: Report a bug or unexpected behavior
title: '[BUG] '
labels: bug
assignees: ''

---

## Bug Description

A clear and concise description of what the bug is.

## Steps to Reproduce

1. Go to '...'
2. Click on '...'
3. Execute '...'
4. See error

## Expected Behavior

A clear description of what you expected to happen.

## Actual Behavior

What actually happened.

## Minimal Reproducible Example

```python
# Paste minimal code that reproduces the issue
from pulseechogui import ShapedPulseSequence
import numpy as np

# Your code here
```

## Error Message

```
Paste full error message and traceback here
```

## Environment

- **OS**: [e.g., macOS 14.0, Ubuntu 22.04, Windows 11]
- **Python version**: [e.g., 3.8.10]
- **PulseEchoGui version**: [e.g., 1.0.0]
- **Installation method**: [pip install, pip install -e ., direct script]

**Dependency versions** (run `pip list | grep -E "numpy|scipy|matplotlib|joblib"`):
```
numpy==...
scipy==...
matplotlib==...
joblib==...
```

## Additional Context

Add any other context about the problem here (screenshots, related issues, etc.).

## Checklist

- [ ] I have checked existing issues for duplicates
- [ ] I have tested with the latest version
- [ ] I have provided a minimal reproducible example
- [ ] I have included the full error message
- [ ] I have specified my environment details
